from math import ceil

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder


def search_vacancy_keyboard(total: int, page: int, form_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    next_page = page + 1 if page < total else 1
    prev_page = page - 1 if page >= 1 else total

    kb.button(text='Подать заявку', callback_data=f'send_application_{form_id}')
    kb.button(text='<<', callback_data=f'search_{prev_page}')
    kb.button(text='>>', callback_data=f'search_{next_page}')
    kb.button(text='Изменить фильтры', callback_data='set_filters')
    kb.button(text='В меню', callback_data='start')

    kb.adjust(1, 2, 1, 1)

    return kb.as_markup()
