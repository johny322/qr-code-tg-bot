import datetime
import os

import pandas as pd
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import User, Admin
from misc.async_wraps import run_blocking_io

from config import engine


def add_person(user: User):
    """
    Добавление юзера в бд

    :param user:
    :return:
    """
    with Session(engine) as s:
        try:
            s.add(user)
            s.commit()
        except IntegrityError:
            update_user(user)


async def async_add_person(user: User):
    """Добавление юзера в бд"""
    return await run_blocking_io(add_person, user)


def update_user(user):
    with Session(engine) as s:
        user_id = user.user_id
        full_name = user.full_name
        user_name = user.user_name
        SRS = user.SRS
        IMEI = user.IMEI
        inv_number = user.inv_number
        phone_number = user.phone_number
        s.query(User).filter(User.user_id == user_id).update({User.full_name: full_name,
                                                              User.user_name: user_name,
                                                              User.SRS: SRS,
                                                              User.IMEI: IMEI,
                                                              User.inv_number: inv_number,
                                                              User.phone_number: phone_number})
        s.commit()


async def async_update_user(user):
    await run_blocking_io(update_user, user)


def set_user_imei(user_id, imei):
    with Session(engine) as s:
        user = s.query(User).filter(User.user_id == user_id).first()
        if user:
            s.query(User).filter(User.user_id == user_id).update({User.IMEI: imei})
        else:
            add_person(User(user_id=user_id, IMEI=imei))
        s.commit()


async def async_set_user_imei(user_id, imei):
    await run_blocking_io(set_user_imei, user_id, imei)


def update_inv_number(user_id, inv_number):
    with Session(engine) as s:
        user = s.query(User).filter(User.user_id == user_id).first()
        if user:
            s.query(User).filter(User.user_id == user_id).update({User.inv_number: inv_number})
        else:
            add_person(User(user_id=user_id, inv_number=inv_number))
        s.commit()


async def async_update_inv_number(user_id, inv_number):
    await run_blocking_io(update_inv_number, user_id, inv_number)


def get_excel(user_id):
    with Session(engine) as s:
        datas = s.query(User).all()
    df = pd.DataFrame({
        'user_id': [data.user_id for data in datas],
        'user_name': [data.user_name for data in datas],
        'full_name': [data.full_name for data in datas],
        'date_create': [data.date_create for data in datas],
        'date_update': [data.date_update for data in datas],
        'TEXT': [data.TEXT for data in datas],
        'IMEI': [data.IMEI for data in datas],
        'inv_number': [data.inv_number for data in datas],
        'device_type': [data.device_type for data in datas],
        'serial_number': [data.serial_number for data in datas],
        'SRS': [data.SRS for data in datas],
        'phone_number': [data.phone_number for data in datas],
        'dismantling': [data.dismantling for data in datas]
    })
    now = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
    path = f'data_{user_id}_{now}.xlsx'
    df.to_excel(path, index=False)
    path = os.path.abspath(path)
    return path


async def async_get_excel(user_id):
    return await run_blocking_io(get_excel, user_id)


def get_admins():
    with Session(engine) as s:
        admins = s.query(Admin).all()
    return [admin.admin_id for admin in admins]


async def async_get_admins():
    return await run_blocking_io(get_admins)


def add_admin(admin: Admin):
    with Session(engine) as s:
        try:
            s.add(admin)
            s.commit()
            return True
        except IntegrityError:
            return False


async def async_add_admin(admin):
    return await run_blocking_io(add_admin, admin)


def set_user_dismantling(user_id, dismantling):
    with Session(engine) as s:
        s.query(User).filter(User.user_id == user_id).update({User.dismantling: dismantling})
        s.commit()
        # user = s.query(User).filter(User.user_id == user_id).first()
        # if user:
        #     s.query(User).filter(User.user_id == user_id).update({User.dismantling: dismantling})
        # else:
        #     add_person(User(user_id=user_id, dismantling=dismantling))
        # s.commit()


async def async_set_user_dismantling(user_id, dismantling):
    await run_blocking_io(set_user_dismantling, user_id, dismantling)


def get_user(user_id) -> User:
    """
    Получить пользователя по id

    :param user_id:
    :return:
    """
    with Session(engine) as s:
        # session = sessionmaker(bind=engine)
        # s = session()
        return s.query(User).filter(User.user_id == user_id).scalar()


async def async_get_user(user_id):
    """Получить пользователя по id"""
    return await run_blocking_io(get_user, user_id)
