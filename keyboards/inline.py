from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from utils.config_loader import MESSAGES, BUTTONS
from states.pagination import Pagination
from utils.db import get_posts_list


async def start_inline():
    keyboard = InlineKeyboardBuilder()
    buttons = BUTTONS['start']

    for button_i in range(1, len(buttons) + 1):
        keyboard.button(text=buttons[f'{button_i}']['text'], callback_data=buttons[f'{button_i}']['callback'])
    keyboard.adjust(2)

    return keyboard.as_markup()


async def back_start_menu_inline():
    keyboard = InlineKeyboardBuilder()
    button = BUTTONS['back_start_menu']

    keyboard.button(text=button['text'], callback_data=button['callback'])

    return keyboard.as_markup()


async def profile_inline():
    keyboard = InlineKeyboardBuilder()
    buttons = BUTTONS['profile']

    for button_i in range(1, len(buttons) + 1):
        keyboard.button(text=buttons[f'{button_i}']['text'], callback_data=buttons[f'{button_i}']['callback'])
    keyboard.adjust(2)

    return keyboard.as_markup()


async def my_referrals_inline():
    keyboard = InlineKeyboardBuilder()

    button = BUTTONS['my_referrals']

    keyboard.button(text=button['text'], callback_data=button['callback'])

    return keyboard.as_markup()


async def cancel_top_up_inline():
    keyboard = InlineKeyboardBuilder()

    button = BUTTONS['cancel_top_up']

    keyboard.button(text=button['text'], callback_data=button['callback'])

    return keyboard.as_markup()


async def posts_list_inline(user_id, page=0, paginate_index=10):
    keyboard = InlineKeyboardBuilder()

    posts_list = await get_posts_list(user_id)
    start_offset = page * paginate_index
    end_offset = start_offset + paginate_index

    for post in posts_list[start_offset:end_offset]:
        is_active = "🟢 Активен" if post[4] == True else "🔴 Не активен"
        keyboard.row(InlineKeyboardButton(text=f'ID {post[0]} | {is_active}', callback_data=f'post_{post[0]}'))

    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=Pagination(page=page - 1).pack(),
            )
        )
    if end_offset < len(posts_list):
        buttons_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=Pagination(page=page + 1).pack(),
            )
        )

    keyboard.row(*buttons_row)

    return keyboard.as_markup()


async def edit_post_opportunity(post_id, is_active):
    keyboard = InlineKeyboardBuilder()

    buttons = BUTTONS['edit_post_opportunity']

    keyboard.button(text=buttons['1']['text'], callback_data=buttons['1']['callback'].format(post_id=post_id))
    keyboard.button(text=buttons['3']['text'], callback_data=buttons['3']['callback'].format(post_id=post_id))

    if is_active == 0:
        keyboard.button(text=buttons['4']['text'], callback_data=buttons['4']['callback'].format(post_id=post_id))

    keyboard.button(text=buttons['2']['text'], callback_data=buttons['2']['callback'])

    keyboard.adjust(1)

    return keyboard.as_markup()


async def autoposting_types():
    keyboard = InlineKeyboardBuilder()

    buttons = BUTTONS['autoposting_types']

    keyboard.button(text=buttons['1']['text'], callback_data=buttons['1']['callback'])
    keyboard.button(text=buttons['2']['text'], callback_data=buttons['2']['callback'])

    keyboard.adjust(1)

    return keyboard.as_markup()


async def autoposting_buy_or_no(post_type):
    keyboard = InlineKeyboardBuilder()

    buttons = BUTTONS['autoposting_buy_or_no']

    keyboard.button(text=buttons['1']['text'], callback_data=buttons["1"]["callback"].format(post_type=post_type))
    keyboard.button(text=buttons['2']['text'], callback_data=buttons['2']['callback'])

    keyboard.adjust(1)

    return keyboard.as_markup()