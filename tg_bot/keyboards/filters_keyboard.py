from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


def get_filters(back: str, find: str, feel_lucky: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    adjust = [3, 1, 1]
    kb.button(text='Роли', callback_data='set_roles')
    kb.button(text='Хакатоны', callback_data='set_hacks')
    kb.button(text='Технологии', callback_data='set_techs')

    kb.button(text='Найти', callback_data=find)
    if feel_lucky:
        kb.button(text='Мне повезёт!', callback_data=feel_lucky)
        adjust.append(1)
    kb.button(text='Назад', callback_data=back)
    kb.adjust(*adjust)
    return kb.as_markup()


def drop_techs_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='Сбросить технологии', callback_data='drop_techs')
    return kb.as_markup()
