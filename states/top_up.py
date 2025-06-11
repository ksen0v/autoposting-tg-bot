from aiogram.fsm.state import State, StatesGroup

class TopUp(StatesGroup):
    amount = State()