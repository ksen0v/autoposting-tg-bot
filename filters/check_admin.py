from aiogram.filters import BaseFilter
from aiogram.types import Message

from utils.db import get_all_is_admin
from utils.logger import logger


class AdminFilter(BaseFilter):
    def __init__(self):
        self.admin_ids = []

    async def update(self):
        self.admin_ids = await get_all_is_admin()
        logger.info(f'Updated admin list: {self.admin_ids}')

    async def __call__(self, message: Message):
        try:
            return message.from_user.id in self.admin_ids
        except:
            pass


admin_filter = AdminFilter()
