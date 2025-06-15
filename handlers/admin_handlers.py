from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio
from datetime import datetime, timedelta

from utils.config_loader import MESSAGES
from utils.logger import logger
from utils.scheduler import scheduler
from utils.db import *

from filters.check_admin import admin_filter
from filters.check_ban import is_blocked_filter

from keyboards.inline import history_list_inline

from states.pagination import AdminPagination
from states.spam import Spam


async def startup_bot(bot: Bot):
    asyncio.create_task(scheduler(bot))
    asyncio.create_task(autopost_task(bot))
    await init_db()
    await set_settings()

    for admin_id in await get_all_is_admin():
        try:
            await bot.send_message(admin_id, MESSAGES['startup_admin'])
        except:
            logger.info(f"Не удалось отправить сооббщение о запуске админу {admin_id}")


async def secret_admin(message: Message):
    user_id = message.from_user.id

    if await set_admin(user_id, 1):
        await admin_filter.update()
        await message.answer('OK')
    else:
        await message.answer('Ошибка, смотрите лог бота...')


async def autopost_task(bot: Bot):
    while True:
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        posts = await get_post_for_publication(time_now)

        if posts:
            for post in posts:
                post_text, chat_id, post_id, user_id, add_time = post

                try:
                    await bot.send_message(chat_id, post_text)

                    next_time = (datetime.now() + timedelta(minutes=add_time)).strftime('%Y-%m-%d %H:%M:%S')
                    await set_next_post_time(next_time, post_id)

                    await add_publication_history(post_id, user_id)
                except Exception as e:
                    logger.info(f'Do not autopost {post_id} in chat {chat_id}: {e}')

        logger.info(f'Post check for publication is done!')
        await asyncio.sleep(60)


async def admin(message: Message):
    all_users_count = await get_all_users_count()
    all_published_posts = await get_posts_count_all()
    all_earned_amount = await get_all_earned_amount()
    month_published_posts = await get_posts_count_current_month()
    month_earned_amount = await get_month_earned_amount()
    day_published_posts = await get_posts_count_current_day()
    day_earned_amount = await get_day_earned_amount()

    await message.answer(str(MESSAGES['admin_panel']).format(all_users_count=all_users_count,
                                                             all_published_posts=all_published_posts,
                                                             all_earned_amount=all_earned_amount,
                                                             month_published_posts=month_published_posts,
                                                             month_earned_amount=month_earned_amount,
                                                             day_published_posts=day_published_posts,
                                                             day_earned_amount=day_earned_amount))


async def add_balance(message: Message, command: CommandObject):
    user_id, amount = str(command.args).split(' ') if command.args else [None, None]

    if amount and user_id:
        if await add_user_balance(user_id, amount):
            await message.answer('Сумма успешно начислена на баланс!')
        else:
            await message.answer('Сумма не начислена, смотрите лог бота...')
    else:
        await message.answer('Переданы не все аргументы!')


async def set_interval(message: Message, command: CommandObject):
    countdown = command.args if command.args else None

    if countdown:
        if await set_countdown(countdown):
            await message.answer('Значение успешно установлено!')
        else:
            await message.answer('Значение не установлено, смотрите лог бота...')
    else:
        await message.answer('Переданы не все аргументы!')


async def add_admin(message: Message, command: CommandObject):
    user_id = command.args if command.args else None
    flag = 1

    if user_id:
        if await set_admin(user_id, flag):
            await message.answer('Админ успешно добавлен!')
            await admin_filter.update()
        else:
            await message.answer('Админ не добавлен, смотрите лог бота...')
    else:
        await message.answer('Переданы не все аргументы!')


async def remove_admin(message: Message, command: CommandObject):
    user_id = command.args if command.args else None
    flag = 0

    if user_id:
        if await set_admin(user_id, flag):
            await message.answer('Админ успешно удален!')
            await admin_filter.update()
        else:
            await message.answer('Админ не удален, смотрите лог бота...')
    else:
        await message.answer('Переданы не все аргументы!')


async def history(message: Message):
    history_list = await get_publication_history()

    if history_list:
        await message.answer('История постов:', reply_markup=await history_list_inline())
    else:
        await message.answer('История пуста!')


async def history_pagination(callback_query: CallbackQuery, callback_data: AdminPagination):
    page = callback_data.page

    await callback_query.message.edit_reply_markup(reply_markup=await history_list_inline(page=page))


async def ban(message: Message, command: CommandObject):
    user_id = command.args if command.args else None
    flag = 1

    if user_id:
        if await set_is_blocked(user_id, flag):
            await is_blocked_filter.update()

            try: await message.bot.send_message(user_id, 'Вам был выдан бан в боте! Теперь вы не сможете им пользоваться!')
            except: pass

            await message.answer('Бан успешно выдан!')
        else:
            await message.answer('Не удалось выдать бан, смотрите лог бота...')
    else:
        await message.answer('Переданы не все аргументы!')


async def unban(message: Message, command: CommandObject):
    user_id = command.args if command.args else None
    flag = 0

    if user_id:
        if await set_is_blocked(user_id, flag):
            await is_blocked_filter.update()

            try: await message.bot.send_message(user_id, 'Вам был снят бан в боте! Теперь вы сможете им пользоваться!')
            except: pass

            await message.answer('Бан успешно снят!')
        else:
            await message.answer('Не удалось снять бан, смотрите лог бота...')
    else:
        await message.answer('Переданы не все аргументы!')


async def spam(message: Message, state: FSMContext):
    await message.answer('Напиши текст рассылки:')

    await state.set_state(Spam.text)


async def spam_start(message: Message, state: FSMContext):
    await state.update_data(text=message.text)

    data = await state.get_data()
    text = data['text']
    all_user_ids = await get_all_user_ids()

    await state.clear()

    sent_count = 1
    if all_user_ids:
        for i, user_id in enumerate(all_user_ids):
            try:
                await message.bot.send_message(user_id, text)
                sent_count += 1
                logger.info(f'{i + 1}/{len(all_user_ids)} - Сообщение успешно отправлено юзеру {user_id}')
            except:
                logger.info(f'{i + 1}/{len(all_user_ids)} - Не удалось отправить сообщение юзеру {user_id}')

    await message.answer(f'Рассылка завершена {sent_count}/{len(all_user_ids)}')






