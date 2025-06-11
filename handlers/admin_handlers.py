from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.types import Message
import asyncio
from datetime import datetime, timedelta

from utils.config_loader import MESSAGES, ADMIN_ID, COUNTDOWN
from utils.logger import logger
from utils.scheduler import scheduler
from utils.db import init_db, add_balance, get_post_for_publication, set_next_post_time

from utils.db import *


async def startup_bot(bot: Bot):
    asyncio.create_task(scheduler(bot))
    asyncio.create_task(autopost_task(bot))
    await init_db()

    try:
        await bot.send_message(ADMIN_ID, MESSAGES['startup_admin'])
    except:
        logger.info(f"Не удалось отправить сооббщение о запуске админу {ADMIN_ID}")


async def admin_add_balance(message: Message, command: CommandObject):
    admin_id = message.from_user.id
    amount = command.args

    if admin_id == int(ADMIN_ID):
        await add_balance(admin_id, amount)


async def autopost_task(bot: Bot):
    while True:
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        posts = await get_post_for_publication(time_now)

        if posts:
            for post in posts:
                post_text, chat_id, post_id = post

                try:
                    await bot.send_message(chat_id, post_text)

                    next_time = (datetime.now() + timedelta(seconds=COUNTDOWN)).strftime('%Y-%m-%d %H:%M:%S')
                    await set_next_post_time(next_time, post_id)
                except Exception as e:
                    logger.info(f'Do not autopost {post_id} in chat {chat_id}: {e}')

        logger.info(f'Post check for publication is done!')
        await asyncio.sleep(60)
