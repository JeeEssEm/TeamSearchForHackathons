from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU


button_yes = KeyboardButton(text=LEXICON_RU['yes_button'])
button_no = KeyboardButton(text=LEXICON_RU['no_button'])

my_teams_button = KeyboardButton(text=LEXICON_RU['my_teams'])
my_form_button = KeyboardButton(text=LEXICON_RU['my_form'])
edit_my_form_button = KeyboardButton(text=LEXICON_RU['edit_my_form'])

yes_no_kb_builder = ReplyKeyboardBuilder()
yes_no_kb_builder.row(button_yes, button_no, width=2)

kb_1_builder = ReplyKeyboardBuilder()
kb_1_builder.row(my_teams_button, my_form_button, width=2)

kb_2_builder = ReplyKeyboardBuilder()
kb_2_builder.row(edit_my_form_button, width=2)

yes_no_kb: ReplyKeyboardMarkup = yes_no_kb_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

kb_1: ReplyKeyboardMarkup = kb_2_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

kb_1: ReplyKeyboardMarkup = kb_1_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)
