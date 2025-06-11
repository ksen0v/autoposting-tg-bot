import asyncio

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext

from keyboards.inline import *
from utils.config_loader import MESSAGES, BOT_USERNAME, PRICES, CHAT_ID
from utils.db import *
from utils.tools import *
from utils.crypto_bot import *
from states.top_up import TopUp
from states.pagination import Pagination
from states.post import EditTextPost, CreatePost


# START BLOCK
async def start(message: Message, command: CommandObject):
    if command.args:
        inviter_user_id, inviter_username = command.args, await get_username(command.args)  # USER ID (INVITER)
        referral_user_id, referral_username = message.from_user.id, message.from_user.username  # NEW USER ID (REFERRAL)

        if await register_user(referral_user_id, referral_username, inviter_user_id):
            await message.bot.send_message(inviter_user_id,
                                           str(MESSAGES['new_referral_inviter']).format(username=referral_username))
            await message.answer(str(MESSAGES['new_referral']).format(username=inviter_username))
        else:
            await message.answer(MESSAGES['error_referral'])
    else:
        await register_user(message.from_user.id, message.from_user.username)

    await message.answer(MESSAGES['start'], reply_markup=await start_inline())


async def start_query(callback_query: CallbackQuery):
    await callback_query.message.answer(MESSAGES['start'], reply_markup=await start_inline())
    await callback_query.answer()


# INFORMATION BLOCK
async def information(callback_query: CallbackQuery):
    await callback_query.message.answer(MESSAGES['information'], reply_markup=await back_start_menu_inline())
    await callback_query.answer()


# PROFILE BLOCK
async def profile(callback_query: CallbackQuery):
    user_id, username, balance, active_posts, registration_date, invited_by = await get_profile_info(
        callback_query.from_user.id)
    invited_by_username = f'@{await get_username(invited_by)}' if invited_by else 'Нет'

    await callback_query.message.answer(str(MESSAGES['profile']).format(name=username,
                                                                        user_id=user_id,
                                                                        balance=balance,
                                                                        active_posts=active_posts,
                                                                        registration_date=registration_date,
                                                                        invited_by=invited_by_username),
                                        reply_markup=await profile_inline())
    await callback_query.answer()


async def top_up(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(MESSAGES['top_up_amount'], reply_markup=await cancel_top_up_inline())
    await callback_query.answer()
    await state.set_state(TopUp.amount)


async def top_up_get_invoice(message: Message, state: FSMContext = None, amount=0):
    if amount == 0:
        await state.update_data(amount=message.text)
        data = await state.get_data()
        amount_data = data.get('amount')

        await get_invoice(message, amount_data)
    else:
        await get_invoice(message, amount)


async def cancel_top_up(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await profile(callback_query)


async def ref_system(callback_query: CallbackQuery):
    total_refs, earned = await get_referral_info(callback_query.from_user.id)
    ref_link = f'https://t.me/{BOT_USERNAME}?start={callback_query.from_user.id}'

    await callback_query.message.answer(str(MESSAGES['ref_system']).format(total_refs=total_refs,
                                                                           earned=earned,
                                                                           ref_link=ref_link),
                                        reply_markup=await my_referrals_inline())
    await callback_query.answer()


async def my_referrals(callback_query: CallbackQuery):
    referrals_list = await get_referrals_list(callback_query.from_user.id)
    referrals_list_fixed = await format_referrals_list(referrals_list, 10)

    if referrals_list:
        for paginate_referrals in referrals_list_fixed:
            await callback_query.message.answer(
                str(MESSAGES['referrals_list']).format(referrals_list="\n".join(paginate_referrals)))
    else:
        await callback_query.message.answer(MESSAGES['no_referrals'])

    await callback_query.answer()


# MY POSTS BLOCK
async def my_posts(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    posts_list = await get_posts_list(user_id)

    if posts_list:
        await callback_query.message.answer(str(MESSAGES['my_posts']), reply_markup=await posts_list_inline(user_id))
    else:
        await callback_query.message.answer(MESSAGES['my_posts_no'])

    await callback_query.answer()


async def my_posts_no_query(message: Message, user_id):
    posts_list = await get_posts_list(user_id)

    if posts_list:
        await message.answer(str(MESSAGES['my_posts']), reply_markup=await posts_list_inline(user_id))
    else:
        await message.answer(MESSAGES['my_posts_no'])


async def my_posts_pagination(callback_query: CallbackQuery, callback_data: Pagination):
    user_id = callback_query.from_user.id
    page = callback_data.page

    await callback_query.message.edit_reply_markup(reply_markup=await posts_list_inline(user_id, page))

    await callback_query.answer()


async def post_details(callback_query: CallbackQuery):
    post_id = callback_query.data.split('_')[1]
    post = await get_post(post_id)
    is_active = "🟢 Активен" if post[3] == True else "🔴 Не активен"
    type_post = "С ссылкой" if post[4] == 'link' else "Без ссылки"

    await callback_query.message.answer(str(MESSAGES['post_details']).format(post_id=post_id,
                                                                             post_text=post[0],
                                                                             chat_id=post[1],
                                                                             add_time=post[2],
                                                                             type_post=type_post,
                                                                             expiry_date=post[5],
                                                                             next_post_time=post[6],
                                                                             is_active=is_active),
                                        reply_markup=await edit_post_opportunity(post_id, post[3]))

    await callback_query.answer()


async def post_details_no_query(message: Message, post_id):
    post = await get_post(post_id)
    is_active = "🟢 Активен" if post[3] == True else "🔴 Не активен"
    type_post = "С ссылкой" if post[4] == 'link' else "Без ссылки"

    await message.answer(str(MESSAGES['post_details']).format(post_id=post_id,
                                                              post_text=post[0],
                                                              chat_id=post[1],
                                                              add_time=post[2],
                                                              type_post=type_post,
                                                              expiry_date=post[5],
                                                              next_post_time=post[6],
                                                              is_active=is_active),
                         reply_markup=await edit_post_opportunity(post_id, post[3]))


async def renew_post(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    post_id = callback_query.data.split('_')[1]
    post_type = await get_type_post(post_id)
    link_post_price = PRICES['link_post_price']
    no_link_post_price = PRICES['no_link_post_price']

    if post_type == 'link':
        if await get_balance(callback_query.from_user.id) >= link_post_price:
            await remove_balance(user_id, link_post_price)
            await set_is_active_post(post_id, 1)
            await add_active_posts(user_id)
            await callback_query.message.answer(MESSAGES['renew_post_successful'])
        else:
            await callback_query.message.answer(MESSAGES['buy_autoposting_error'])
    else:
        if await get_balance(callback_query.from_user.id) >= no_link_post_price:
            await remove_balance(user_id, no_link_post_price)
            await set_is_active_post(post_id, 1)
            await add_active_posts(user_id)
            await callback_query.message.answer(MESSAGES['buy_autoposting_successful'])
        else:
            await callback_query.message.answer(MESSAGES['buy_autoposting_error'])

    await callback_query.answer()


async def change_post_text(callback_query: CallbackQuery, state: FSMContext):
    post_id = callback_query.data.split('_')[1]

    await callback_query.message.answer(MESSAGES['edit_enter_text'])
    await state.set_state(EditTextPost.text)
    await state.update_data(id=post_id)

    await callback_query.answer()


async def change_post_text_proceed(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    text = data['text']
    post_id = data['id']
    user_id = message.from_user.id
    type_post = await get_type_post(post_id)

    if await is_contain_link(text) and type_post == 'no_link':
        await message.bot.send_message(user_id, MESSAGES['edit_text_error_link'])
    else:
        await edit_post_text(post_id, text)
        await message.bot.send_message(user_id, MESSAGES['edit_text_successful'])
        await post_details_no_query(message, post_id)
        await state.clear()


async def delete_post(callback_query: CallbackQuery):
    post_id = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id

    if await remove_post(post_id):
        await remove_active_posts(user_id)
        await callback_query.message.answer(MESSAGES['remove_successful'])
    else:
        await callback_query.message.answer(MESSAGES['remove_error'])

    await my_posts_no_query(callback_query.message, callback_query.from_user.id)
    await callback_query.answer()


# AUTO POSTING BLOCK

async def autoposting(callback_query: CallbackQuery):
    await callback_query.message.answer(MESSAGES['autoposting_choose'], reply_markup=await autoposting_types())
    await callback_query.answer()


async def autoposting_link(callback_query: CallbackQuery):
    await callback_query.message.answer(MESSAGES['autoposting_link'], reply_markup=await autoposting_buy_or_no('link'))
    await callback_query.answer()


async def autoposting_no_link(callback_query: CallbackQuery):
    await callback_query.message.answer(MESSAGES['autoposting_no_link'],
                                        reply_markup=await autoposting_buy_or_no('no_link'))
    await callback_query.answer()


async def autoposting_buy(callback_query: CallbackQuery, state: FSMContext):
    post_type = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    link_post_price = PRICES['link_post_price']
    no_link_post_price = PRICES['no_link_post_price']

    if post_type == 'link':
        if await get_balance(callback_query.from_user.id) >= link_post_price:
            await remove_balance(user_id, link_post_price)
            await callback_query.message.answer(MESSAGES['buy_autoposting_successful'])
            await autoposting_add_post_text(callback_query, state, post_type='link')
        else:
            await callback_query.message.answer(MESSAGES['buy_autoposting_error'])
    else:
        if await get_balance(callback_query.from_user.id) >= no_link_post_price:
            await remove_balance(user_id, no_link_post_price)
            await callback_query.message.answer(MESSAGES['buy_autoposting_successful'])
            await autoposting_add_post_text(callback_query, state, 'no_link')
        else:
            await callback_query.message.answer(MESSAGES['buy_autoposting_error'])

    await callback_query.answer()


async def autoposting_add_post_text(callback_query: CallbackQuery, state: FSMContext, post_type='no_link'):
    await callback_query.message.answer(MESSAGES['autoposting_add_post_text'])

    await state.set_state(CreatePost.post_text)
    await state.update_data(post_type=post_type)

    await callback_query.answer()


async def autoposting_add_post(message: Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    data = await state.get_data()
    post_type = data['post_type']
    post_text = data['post_text']
    user_id = message.from_user.id

    if await is_contain_link(post_text) and post_type == 'no_link':
        await message.bot.send_message(user_id, MESSAGES['edit_text_error_link'])
    else:
        await add_post(user_id, post_text, CHAT_ID, 30, True, post_type)
        await add_active_posts(user_id)
        await message.bot.send_message(user_id, MESSAGES['autoposting_post_added'])
        await state.clear()


async def check_expired_posts(bot: Bot):
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    expired_posts = await get_expired_posts(time_now)

    if expired_posts:
        for post in expired_posts:
            post_id, user_id = post

            await set_is_active_post(post_id, 0)
            await remove_active_posts(user_id, 1)

            try:
                await bot.send_message(user_id, str(MESSAGES['expire_date_post']).format(post_id=post_id))
                logger.info(f'Deactivate user ({user_id}) post {post_id} via time over!')
            except Exception as e:
                logger.info(f'Do not send message user {user_id} for deactive post {post_id} via time over: {e}')