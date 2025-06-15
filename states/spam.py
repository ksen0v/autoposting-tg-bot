from aiogram.fsm.state import StatesGroup, State


class Spam(StatesGroup):
    text = State()