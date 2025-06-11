from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix="pag"):
    page: int