from aiogram import BaseMiddleware
from aiogram.types import Message, Chat


class PrivateOnlyMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            chat = event.chat
            if chat.type != "private":
                return
        return await handler(event, data)