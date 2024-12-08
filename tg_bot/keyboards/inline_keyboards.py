from aiogram import F
from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from dependency_injector.wiring import Provide, inject

from core.services import TeamsService, UsersService
from core.dependencies.container import Container
from core.repositories import TeamsRepository, UsersRepository
from core import dtos

from lexicon.lexicon_ru import LEXICON_RU

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
    for i, j in enumerate(tech_data):
        print(j.lower().startswith(letter))
        if j.upper().startswith(letter):
            kb.button(text=f'{'✅ ' if i in selected_technologies else '❌ '}{j}', callback_data=f'technology_{i}')
            print(f'{'✅ ' if i in selected_technologies else '❌ '}{j}')
            print(f'technology_{i}')
    kb.button(text='Назад', callback_data='back')
    kb.adjust(1)
    return kb.as_markup()


def create_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='Моя анкета', callback_data='my_forms')
    kb.button(text='Мои команды', callback_data='my_teams')
    kb.button(text='Редактировать анкету', callback_data='new_form')
    kb.button(text='Создать команду', callback_data='new_team')
    kb.button(text='Искать анкеты', callback_data='search_form')
    kb.button(text='Искать команды', callback_data='search_team')
    kb.adjust(2)
    return kb.as_markup()


@inject
async def my_teams_keyboard(user_id: int, db=Provide[Container.db]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async with db.session() as session:
        user_repo = UsersRepository(session)
        teams = await user_repo.get_teams(user_id)

    for team in teams:
        kb.button(text=team['title'], callback_data=f'team_{team["id"]}')
    kb.button(text='Назад', callback_data='back')
    kb.adjust(2)
    return kb.as_markup()


@inject
async def my_team_keyboard(user_id: int, team_id: int, db=Provide[Container.db]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async with db.session() as session:
        team_repo = TeamsRepository(session)
        my_team = await team_repo.get_by_id(team_id)
        members = my_team.members
        if not (my_team.captain_id == user_id and len(members) <= 1):
            kb.button(text="Покинуть команду", callback_data=f'leave_team_{team_id}')
    if my_team.captain_id == user_id:
        kb.button(text='Редактировать команду', callback_data=f'edit_team_{team_id}')
    kb.button(text='Участники', callback_data=f'members_{team_id}')
    if my_team.captain_id == user_id:
        kb.button(text='Создать вакансию', callback_data=f'create_vacancy_{team_id}')
    kb.button(text='Вакансии', callback_data=f'vacancies_{team_id}')
    kb.button(text='Назад', callback_data='my_teams')
    kb.adjust(2)
    return kb.as_markup()


@inject
async def team_users_keyboard(user_id: int, team_id: int, offset: int = 0, db=Provide[Container.db]) -> tuple[InlineKeyboardMarkup, list[dtos.BaseUser]]:
    kb = InlineKeyboardBuilder()
    async with db.session() as Session:
        team_repo = TeamsRepository(Session)
        team = await team_repo.get_by_id(team_id)
    members = team.members

    if offset < 0:
        offset = len(members) - 1
    if team.captain_id == user_id and members[offset].id != team.captain_id:
        kb.button(text='Исключить участника', callback_data=f'kick_{team_id}_{members[offset].id}')
        kb.button(text='Сделать капитаном', callback_data=f'make_captain_{team_id}_{members[offset].id}')

    kb.button(text='<<', callback_data=f'members_{team.id}_{offset - 1}')
    kb.button(text='>>', callback_data=f'members_{team.id}_{(offset + 1) % len(members)}')
    kb.button(text='Назад', callback_data=f'team_{team_id}')
    kb.adjust(2)
    return kb.as_markup(), members[offset]


def my_form_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Редактировать имя', callback_data='my_form_edit_name')
    kb.button(text='Редактировать отчество', callback_data='my_form_edit_middlename')
    kb.button(text='Редактировать фамилию', callback_data='my_form_edit_surname')
    kb.button(text='Редактировать университет', callback_data='my_form_edit_uni')
    kb.button(text='Редактировать курс', callback_data='my_form_edit_course')
    kb.button(text='Редактировать учебную группу', callback_data='my_form_edit_group')
    kb.button(text='Редактировать информацию себе', callback_data='my_form_edit_about_me')
    kb.button(text='Редактировать стек технологий', callback_data='my_form')
    kb.button(text='Редактировать роли', callback_data='my_form')

    kb.button(text='Назад', callback_data='start')
    kb.adjust(2)
    return kb.as_markup()


def my_form_edit_field_keyboard(back: str, delete: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data=back)
    if delete:
        kb.button(text='Удалить поле', callback_data=delete)
    kb.adjust(2)
    return kb.as_markup()


# async def check_vacancies(user_id: int, vacancy_id: int, team_id:int, offset: int = 0) -> tuple[InlineKeyboardMarkup, str]:
#     kb = InlineKeyboardBuilder()
#     my_team = await Team.get(Team.id == team_id)
#     if my_team.captain_id == user_id:
#         kb.button(text='Изменить', callback_data=f'edit_vacancy_{vacancy_id}')
#         kb.button(text='Удалить', callback_data=f'delete_{vacancy_id}')
#     kb.button(text='<<', callback_data='backward')
#     kb.button(text='>>', callback_data='forward')
#     kb.adjust(2)
#     return kb.as_markup(), str(offset)
#
#
# async def edit_team(team_id: int) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text='Название', callback_data=f'edit_team_name_{team_id}')
#     kb.button(text='Аватар', callback_data=f'edit_team_avatar_{team_id}')
#     kb.button(text='Описание', callback_data=f'edit_team_description_{team_id}')
#     kb.adjust(2)
#     return kb.as_markup()




