from aiogram import Bot
import asyncio

from handlers.user_handlers import check_expired_posts
from utils.logger import logger
from utils.config_loader import COUNTDOWN_POST_CHECK


async def scheduler(bot: Bot):
    while True:
        await check_expired_posts(bot)
        logger.info(f'Post check is done!')
        await asyncio.sleep(COUNTDOWN_POST_CHECK)