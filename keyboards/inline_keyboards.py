from aiogram import F
from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_RU
from database.technologies_data  import tech_data



search_team_button = InlineKeyboardButton(
    text='Найти команду',
    callback_data='Поиск команды...'
)
create_team_button = InlineKeyboardButton(
    text='Создать команду',
)



backward_button = InlineKeyboardButton(
    text='<<'
)
forward_button = InlineKeyboardButton(
    text='>>'
)
send_appl_button = InlineKeyboardButton(
    text=LEXICON_RU['send_appl']
)

keyboard_1 = InlineKeyboardMarkup(
    inline_keyboard=[[search_team_button],
                     [create_team_button]]
)
keyboard_2 = InlineKeyboardMarkup(
    inline_keyboard=[[backward_button], [send_appl_button], [forward_button]]
)

def alphabet_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i in range(65, 91):
        kb.button(text=chr(i), callback_data=f'technologies_{chr(i)}')
    kb.adjust(5)
    return kb.as_markup()

def choose_technologies(letter: str, selected_technologies: list[int]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i,j in enumerate(tech_data):
        print(j.lower().startswith(letter))
        if j.upper().startswith(letter):
            kb.button(text=f'{'✅ ' if i in selected_technologies else '❌ '}{j}', callback_data=f'technology_{i}')
            print(f'{'✅ 'if i in selected_technologies else '❌ '}{j}')
            print(f'technology_{i}')
    kb.button(text='Назад', callback_data='back')
    kb.adjust(1)
    return kb.as_markup()

