from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

import aiosend
from aiosend import CryptoPay

from handlers.admin_handlers import *
from handlers.user_handlers import *

from utils.env import BOT_TOKEN, CRYPTO_BOT_TOKEN

from states.top_up import TopUp
from states.post import EditTextPost
from states.pagination import Pagination

from middlewares.private_chat import PrivateOnlyMiddleware

storage = MemoryStorage()
bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(storage=storage)
cp = CryptoPay(CRYPTO_BOT_TOKEN, network=aiosend.MAINNET)


async def main():

    #ADMIN HANDLERS
    dp.startup.register(startup_bot)
    dp.message.register(admin_add_balance, Command('admin_add_balance'))

    #START HANDLERS
    dp.message.register(start, Command('start'))

    #AUTOPOSTING HANDLERS
    dp.callback_query.register(autoposting, F.data == 'autoposting')
    dp.callback_query.register(autoposting_link, F.data == 'autoposting_link')
    dp.callback_query.register(autoposting_no_link, F.data == 'autoposting_no_link')
    dp.callback_query.register(autoposting_buy, F.data.startswith('post-buy_'))
    dp.message.register(autoposting_add_post, CreatePost.post_text)

    #INFORMATION HANDLERS
    dp.callback_query.register(information, F.data == 'information')

    #PROFILE HANDLERS
    dp.callback_query.register(profile, F.data == 'profile')
    dp.callback_query.register(ref_system, F.data == 'ref_system')
    dp.callback_query.register(top_up, F.data == 'top_up')
    dp.callback_query.register(my_referrals, F.data == 'my_referrals')
    dp.message.register(top_up_get_invoice, TopUp.amount)
    dp.callback_query.register(cancel_top_up, F.data == 'cancel_top_up')
    cp.invoice_polling(handle_payment)

    #MY POSTS HANDLERS
    dp.callback_query.register(my_posts, F.data == 'my_posts')
    dp.callback_query.register(my_posts_pagination, Pagination.filter())
    dp.callback_query.register(post_details, F.data.startswith('post_'))
    dp.callback_query.register(change_post_text, F.data.startswith('change-text_'))
    dp.message.register(change_post_text_proceed, EditTextPost.text)
    dp.callback_query.register(my_posts, F.data == 'back_to_posts_list')
    dp.callback_query.register(delete_post, F.data.startswith('remove_'))
    dp.callback_query.register(renew_post, F.data.startswith('renew-post_'))

    #UTILS HANDLERS
    dp.callback_query.register(start_query, F.data == 'back_start_menu')

    #MIDDLEWARES
    dp.message.middleware(PrivateOnlyMiddleware())
    dp.callback_query.middleware(PrivateOnlyMiddleware())

    #RUN BOT
    try:
        await asyncio.gather(
            dp.start_polling(bot),
            cp.start_polling(),
        )
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())