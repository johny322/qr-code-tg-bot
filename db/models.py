import datetime

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """таблица с юзерами"""
    __tablename__ = 'Users'

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(250))
    full_name = Column(String(250))
    date_create = Column(DateTime(timezone=True), default=datetime.datetime.now)
    date_update = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)
    TEXT = Column(Text)
    IMEI = Column(BigInteger)
    inv_number = Column(BigInteger)
    device_type = Column(String(250))
    serial_number = Column(String(250))
    SRS = Column(String(250))
    phone_number = Column(String(250))
    dismantling = Column('Демонтаж', String(250))


class Admin(Base):
    __tablename__ = 'Admins'

    admin_id = Column(BigInteger, primary_key=True)
