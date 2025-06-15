from aiogram.filters import BaseFilter
from aiogram.types import Message

from utils.db import get_all_is_blocked
from utils.logger import logger


class IsBlockedFilter(BaseFilter):
    def __init__(self):
        self.blocked_ids = []

    async def update(self):
        self.blocked_ids = await get_all_is_blocked()
        logger.info(f'Updated blocked list: {self.blocked_ids}')

    async def __call__(self, message: Message):
        try:
            return message.from_user.id in self.blocked_ids
        except:
            pass



is_blocked_filter = IsBlockedFilter()

# Создаем инстанс фильтра
#IsAdmin = AdminFilter(admin_ids=asyncio.run(get_all_is_admin()))