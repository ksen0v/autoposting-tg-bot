from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix="pag"):
    page: int


class AdminPagination(CallbackData, prefix="admin_pag"):
    page: int
