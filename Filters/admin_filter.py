from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from db.db_worker import async_get_admins


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.from_user.id in await async_get_admins()