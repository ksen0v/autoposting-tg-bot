from aiosend.types import Invoice

from aiogram.types import Message

from main import cp
from utils.config_loader import MESSAGES, MIN_TOP_UP_AMOUNT
from utils.db import *


async def get_invoice(message: Message, invoice_amount):

    if invoice_amount.isdigit():
        if int(invoice_amount) >= MIN_TOP_UP_AMOUNT:
            invoice = await cp.create_invoice(amount=invoice_amount, 
                                              currency_type='fiat',
                                              fiat='RUB',
                                              expires_in=1200)
            await message.answer(str(MESSAGES['invoice']).format(invoice_id=invoice.invoice_id,
                                                                 invoice_amount=invoice.amount,
                                                                 invoice_link=invoice.bot_invoice_url))
            invoice.poll(message=message)
        else:
            await message.answer(str(MESSAGES['invoice_too_small']).format(min_top_up_amount=MIN_TOP_UP_AMOUNT))
    else:
        await message.answer(MESSAGES['invoice_enter_no_digits'])


async def handle_payment(invoice: Invoice, message: Message):
    user_id = message.from_user.id
    amount = invoice.amount
    inviter_user_id = await get_user_invited_by(user_id)
    earned_amount = amount*0.25

    await add_balance(user_id, amount)
    await add_balance(inviter_user_id, earned_amount)

    await add_earned_amount(inviter_user_id, earned_amount)

    await message.answer(str(MESSAGES['invoice_successful']).format(invoice_amount=amount))
    await message.bot.send_message(inviter_user_id, str(MESSAGES['invoice_ref_system']).format(referral_id=user_id,
                                                                                               invoice_amount=amount,
                                                                                               referral_amount=amount*0.25))

