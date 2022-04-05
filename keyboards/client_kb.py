# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# b1 = KeyboardButton('/Моё местоположение')
# b2 = KeyboardButton('/Отсканировать штрихкод')
# b3 = KeyboardButton('/Ввести номер штрихкода')

# kb_client = ReplyKeyboardMarkup()

# kb_client.add(b1).add(b2).add(b3)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import ADMINS
from db.db_worker import async_get_admins

cancel_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отмена')
        ]
    ],
    resize_keyboard=True
)

general_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отсканировать QR-код')
        ],
        [
            KeyboardButton(text='Ввести данные')
        ],
        [
            KeyboardButton(text='Новая установка оборудования')
        ]
    ],
    resize_keyboard=True
)

admin_general_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отсканировать QR-код')
        ],
        [
            KeyboardButton(text='Ввести данные')
        ],
        [
            KeyboardButton(text='Новая установка оборудования')
        ],
        [
            KeyboardButton(text='Выгрузить базу'), KeyboardButton(text='Добавить админа')
        ]
    ],
    resize_keyboard=True
)

confirm_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Да'), KeyboardButton(text='Нет')
        ]
    ],
    resize_keyboard=True
)


async def get_general_keyboard(id):
    admins = await async_get_admins()
    if id in admins:
        return admin_general_markup
    return general_markup
