from io import BytesIO

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import File
from aiogram.types import InputFile
from aiogram.utils import executor
from aiogram.dispatcher.filters import CommandStart
import os

from Filters.admin_filter import IsAdmin
from config import BOT_TOKEN, engine, ADMINS
from db.db_worker import async_add_person, async_set_user_imei, async_update_user, async_get_excel, async_get_admins, \
    async_add_admin, async_get_user, async_set_user_dismantling, async_update_inv_number
from db.models import User, Base, Admin
from keyboards.client_kb import cancel_markup, confirm_markup, get_general_keyboard
from scan_bot.code_detection import async_detect

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

to_chat_id = '477733380'


@dp.message_handler(CommandStart())
async def start_handler(message: types.Message):
    await message.answer('Добро пожаловать!\nВыберите пункт из меню',
                         reply_markup=await get_general_keyboard(message.from_user.id))


@dp.message_handler(text='Отмена', state='*')
async def cancel_detect(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply('Отмена', reply_markup=await get_general_keyboard(message.from_user.id))


@dp.message_handler(state='new_equipment')
@dp.message_handler(text='Отсканировать QR-код')
async def ar_code_handler(message: types.Message, state: FSMContext):
    state_name = await state.get_state()

    if state_name:
        await message.reply('Пожалуйста отправьте фото кода', reply_markup=cancel_markup)
        await state.set_state(state_name)
    else:
        user = await async_get_user(message.from_user.id)
        if user:
            if user.IMEI or user.inv_number:
                await message.reply('Ваши данные есть в базе',
                                    reply_markup=await get_general_keyboard(message.from_user.id))
                return
        await message.reply('Пожалуйста отправьте фото кода', reply_markup=cancel_markup)
        await state.set_state('get_code')


@dp.message_handler(state='new_equipment', content_types=types.ContentType.PHOTO)
@dp.message_handler(state='get_code', content_types=types.ContentType.PHOTO)
async def detect_code_handler(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    await state.finish()
    # if message.document:
    #     with BytesIO() as buf:
    #         await message.document.download(destination_file=buf)
    #         res = await async_detect(buf)

    # if message.photo:
    # photo: File = await bot.get_file(message.photo[-1].file_id)
    # await photo.download(destination_file='photo1.png')
    # res = await async_detect('photo1.png')
    with BytesIO() as buf:
        await message.photo[-1].download(destination_file=buf)  # загружаем фото из сообщения в буфер
        res = await async_detect(buf)
    if res:
        user = await async_get_user(message.from_user.id)

        res_split = res.split('\n')
        if (len(res_split) > 1) and (res.lower().__contains__('imei')) and (
                res.lower().__contains__("инвентарный номер")):
            imei = res_split[0].split(':')[-1].strip()
            inv_number = res_split[1].split(':')[-1].strip()

            if user:
                dismantling = []
                if (user.IMEI is not None) and (str(user.IMEI) != imei):
                    dismantling.append(imei)
                else:
                    await async_set_user_imei(message.from_user.id, imei)
                if (user.inv_number is not None) and (user.inv_number != inv_number):
                    dismantling.append(inv_number)
                else:
                    await async_update_inv_number(message.from_user.id, inv_number=inv_number)
                print(dismantling)
                if dismantling:
                    await async_set_user_dismantling(message.from_user.id, '\n'.join(dismantling))
            else:
                await async_add_person(User(user_id=message.from_user.id, IMEI=imei, inv_number=inv_number))
        else:
            if user:
                if (user.IMEI is not None) and (str(user.IMEI) != res):
                    await async_set_user_dismantling(message.from_user.id, res)
                else:
                    await async_set_user_imei(message.from_user.id, res)
            else:
                await async_set_user_imei(message.from_user.id, res)
    else:
        res = 'не удалось получить'

    if state_name == 'new_equipment':
        await message.answer(f'Результат: {res}')
        await get_user_data_handler(message, state)
    else:
        await message.answer(f'Результат: {res}', reply_markup=await get_general_keyboard(message.from_user.id))


@dp.message_handler(text='Ввести данные')
async def get_user_data_handler(message: types.Message, state: FSMContext):
    "id клиента, его фио, тип устройства, imei, серийный номер, инвентарный номер, текущая дата, ГРЗ грузового транспортного средства"
    # await message.reply('Пожалуйста введите номер грузового транспортного средства и номер идентификационной карты')
    user = await async_get_user(message.from_user.id)
    if user:
        if user.full_name or user.SRS or user.phone_number:
            await message.reply('Ваши данные есть в базе',
                                reply_markup=await get_general_keyboard(message.from_user.id))
            return
    text = "Пожалуйста введите данные в следующем формате (каждое значение на новой строке):\n" \
           "ФИО\n" \
           "ГРЗ\n" \
           "Номер телефона"
    await message.answer(text, reply_markup=cancel_markup)
    await state.set_state('get_user_data')


@dp.message_handler(state='get_user_data')
async def set_user_data_handler(message: types.Message, state: FSMContext):
    data = message.text.split('\n')
    if len(data) != 3:
        await message.answer('Неверный формат', reply_markup=cancel_markup)
        return
    user_data = {
        'ФИО': data[0],
        'ГРЗ': data[1],
        'Номер телефона': data[2]
    }
    text = "Данные верны?\n" \
           f"ФИО: {data[0]}\n" \
           f"ГРЗ: {data[1]}\n" \
           f"Номер телефона: {data[2]}"
    # names = ['ФИО', 'тип устройства', 'серийный номер', 'инвентарный номер', 'ГРЗ']
    # text = '\n'.join(['Данные верны?'] + [f"{name}: {user_data}" for name, user_data in zip(names, data)])
    await message.answer(text, reply_markup=confirm_markup)
    await state.set_state('set_user_data')
    await state.set_data({
        'user_data': user_data
    })


@dp.message_handler(state='set_user_data', text='Да')
async def save_user_data_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    # await message.answer(data['user_data'], reply_markup=general_markup)
    user = await async_get_user(message.from_user.id)
    if user:
        await async_update_user(User(
            user_id=message.from_user.id,
            user_name=message.from_user.username,
            full_name=data['user_data']['ФИО'],
            SRS=data['user_data']['ГРЗ'],
            phone_number=data['user_data']['Номер телефона'],
            IMEI=user.IMEI,
            inv_number=user.inv_number
        ))
    else:
        user = User(user_id=message.from_user.id,
                    user_name=message.from_user.username,
                    full_name=data['user_data']['ФИО'],
                    SRS=data['user_data']['ГРЗ'],
                    phone_number=data['user_data']['Номер телефона'])
        result = await async_add_person(user)
    await message.answer('Данные внесены', reply_markup=await get_general_keyboard(message.from_user.id))
    # if result:
    #     await message.answer('Данные внесены', reply_markup=general_markup)
    # else:
    #     await message.answer('Вы уже есть в базе', reply_markup=general_markup)


@dp.message_handler(state='set_user_data', text='Нет')
async def save_user_data_handler(message: types.Message, state: FSMContext):
    await get_user_data_handler(message, state)


@dp.message_handler(text='Новая установка оборудования')
async def new_equipment_handler(message: types.Message, state: FSMContext):
    await state.set_state('new_equipment')
    await ar_code_handler(message, state)


@dp.message_handler(state='new_equipment')
async def new_equipment_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await get_user_data_handler(message, state)


@dp.message_handler(IsAdmin(), text='Выгрузить базу')
async def get_excel_handler(message: types.Message):
    excel_path = await async_get_excel(message.from_user.id)
    name = os.path.basename(excel_path)
    report = InputFile(excel_path, name)
    await message.answer_document(report, reply_markup=await get_general_keyboard(message.from_user.id))
    os.remove(excel_path)


@dp.message_handler(IsAdmin(), text='Добавить админа')
async def get_admin_handler(message: types.Message, state: FSMContext):
    await state.set_state('get_admin')
    await message.answer('Введите id админа', reply_markup=cancel_markup)


@dp.message_handler(state='get_admin')
async def set_admin_handler(message: types.Message, state: FSMContext):
    try:
        id = int(message.text)
    except ValueError:
        await message.answer('Неверный формат', reply_markup=cancel_markup)
        await get_admin_handler(message, state)
        return
    text = f'Добавить админа с id: {id}?'
    await message.answer(text, reply_markup=confirm_markup)
    await state.set_state('set_admin')
    await state.set_data({
        'admin_id': id
    })


@dp.message_handler(state='set_admin', text='Да')
async def add_admin_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    admin_id = data['admin_id']
    res = await async_add_admin(Admin(admin_id=admin_id))
    if res:
        await message.answer(f'Админ {admin_id} добавлен',
                             reply_markup=await get_general_keyboard(message.from_user.id))
    else:
        await message.answer(f'Админ {admin_id} уже был добавлен',
                             reply_markup=await get_general_keyboard(message.from_user.id))


@dp.message_handler(state='set_admin', text='Нет')
async def add_admin_handler(message: types.Message, state: FSMContext):
    await get_admin_handler(message, state)


@dp.message_handler(state=None)
async def echo_handler(message: types.Message, state: FSMContext):
    await message.answer(message.text)


async def on_startup(dp):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    dp.filters_factory.bind(IsAdmin)
    for admin_id in ADMINS:
        await async_add_admin(Admin(admin_id=admin_id))
    ADMINS.extend(await async_get_admins())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
