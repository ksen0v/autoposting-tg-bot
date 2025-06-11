from aiogram.fsm.state import State, StatesGroup


class EditTextPost(StatesGroup):
    text = State()
    id = State()


class CreatePost(StatesGroup):
    post_text = State()