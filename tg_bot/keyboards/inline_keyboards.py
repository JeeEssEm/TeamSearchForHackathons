from math import ceil

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
    text="Найти команду", callback_data="Поиск команды..."
)
create_team_button = InlineKeyboardButton(
    text="Создать команду",
)

backward_button = InlineKeyboardButton(text="<<")
forward_button = InlineKeyboardButton(text=">>")
send_appl_button = InlineKeyboardButton(text=LEXICON_RU["send_appl"])

keyboard_1 = InlineKeyboardMarkup(
    inline_keyboard=[[search_team_button], [create_team_button]]
)
keyboard_2 = InlineKeyboardMarkup(
    inline_keyboard=[[backward_button], [send_appl_button], [forward_button]]
)


def alphabet_kb(pos) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i in range(65, 91):
        kb.button(text=chr(i), callback_data=f"technologies_{pos}_{chr(i)}")
    kb.adjust(5)
    kb.button(text="Назад", callback_data="back")
    return kb.as_markup()


def edit_technology_keyboard(pos, techs) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for t in techs:
        kb.button(text=t.title, callback_data=f"technologies_{pos}_{t}")

    return kb.as_markup()


def choose_technologies(
        letter: str, selected_technologies: list[int]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, j in enumerate(tech_data):
        print(j.lower().startswith(letter))
        if j.upper().startswith(letter):
            kb.button(
                text=f"{'✅ ' if i in selected_technologies else '❌ '}{j}",
                callback_data=f"technology_{i}",
            )
            print(f"{'✅ ' if i in selected_technologies else '❌ '}{j}")
            print(f"technology_{i}")
    kb.button(text="Назад", callback_data="back")
    kb.adjust(1)
    return kb.as_markup()


def create_main_keyboard(is_approved: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Моя анкета", callback_data="my_forms")
    kb.button(text="Мои команды", callback_data="my_teams")
    if is_approved:
        kb.button(text="Создать команду", callback_data="new_team")
    kb.button(text="Искать анкеты", callback_data="search_form")
    kb.button(text="Искать команды", callback_data="search_team")
    kb.button(text="Оставить фидбек", callback_data="leave_feedback")
    kb.adjust(2)
    return kb.as_markup()


@inject
async def my_teams_keyboard(
        user_id: int, db=Provide[Container.db]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async with db.session() as session:
        user_repo = UsersRepository(session)
        teams = await user_repo.get_teams(user_id)

    for team in teams:
        kb.button(text=team["title"], callback_data=f'team_{team["id"]}')
    kb.button(text="Назад", callback_data="start")
    kb.adjust(2)
    return kb.as_markup()


@inject
async def my_team_keyboard(
        user_id: int, team_id: int, db=Provide[Container.db]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async with db.session() as session:
        team_repo = TeamsRepository(session)
        my_team = await team_repo.get_by_id(team_id)
        members = my_team.members
        if not (my_team.captain_id == user_id and len(members) <= 1):
            kb.button(text="Покинуть команду",
                      callback_data=f"leave_team_{team_id}")
    if my_team.captain_id == user_id:
        kb.button(text="Редактировать команду",
                  callback_data=f"edit_team_{team_id}")
    kb.button(text="Участники", callback_data=f"members_{team_id}")
    if my_team.captain_id == user_id:
        kb.button(text="Создать вакансию",
                  callback_data=f"create_vacancy_{team_id}")
    kb.button(text="Вакансии", callback_data=f"vacancies_{team_id}")
    kb.button(text="Назад", callback_data="my_teams")
    kb.adjust(2)
    return kb.as_markup()


@inject
async def team_users_keyboard(
        user_id: int, team_id: int, offset: int = 0, db=Provide[Container.db]
) -> tuple[InlineKeyboardMarkup, dtos.TeamMember]:
    kb = InlineKeyboardBuilder()
    async with db.session() as Session:
        team_repo = TeamsRepository(Session)
        team = await team_repo.get_by_id(team_id)
    members = team.members
    adjustment = []
    if offset < 0:
        offset = len(members) - 1
    if team.captain_id == user_id and members[offset].id != team.captain_id:
        kb.button(
            text="Исключить участника",
            callback_data=f"kick_{team_id}_{members[offset].id}",
        )
        kb.button(
            text="Сделать капитаном",
            callback_data=f"make_captain_{team_id}_{members[offset].id}",
        )
        adjustment.append(2)

    if team.captain_id == user_id:
        kb.button(
            text="Поменять роль",
            callback_data=f"change_team_role_{team_id}_{members[offset].id}",
        )
        adjustment.append(1)

    kb.button(text="<<", callback_data=f"members_{team.id}_{offset - 1}")
    kb.button(
        text=">>",
        callback_data=f"members_{team.id}_{(offset + 1) % len(members)}"
    )
    kb.button(text="Назад", callback_data=f"team_{team_id}")

    kb.adjust(*(adjustment + [2, 1]))
    return kb.as_markup(), members[offset]


def my_form_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Редактировать имя", callback_data="my_form_edit_name")
    kb.button(text="Редактировать отчество",
              callback_data="my_form_edit_middlename")
    kb.button(text="Редактировать фамилию",
              callback_data="my_form_edit_surname")
    kb.button(text="Редактировать университет",
              callback_data="my_form_edit_uni")
    kb.button(text="Редактировать курс", callback_data="my_form_edit_course")
    kb.button(text="Редактировать учебную группу",
              callback_data="my_form_edit_group")
    kb.button(
        text="Редактировать информацию себе",
        callback_data="my_form_edit_about_me"
    )
    kb.button(text="Редактировать стек технологий",
              callback_data="my_technologies")
    kb.button(text="Редактировать желаемые хакатоны", callback_data="hacks")
    kb.button(text="Редактировать роли", callback_data="edit_roles")

    kb.button(text="Назад", callback_data="start")
    kb.adjust(2)
    return kb.as_markup()


def my_form_edit_field_keyboard(back: str,
                                delete: str = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=back)
    if delete:
        kb.button(text="Удалить поле", callback_data=delete)
    kb.adjust(2)
    return kb.as_markup()


@inject
async def check_vacancies(
        user_id: int,
        vacancy_id: int,
        team_id: int,
        offset: int = 0,
        db=Provide[Container.db],
) -> tuple[InlineKeyboardMarkup, str]:
    kb = InlineKeyboardBuilder()

    async with db.session() as session:
        team_repo = TeamsRepository(session)
        team = await team_repo.get_by_id(team_id)
    vacancies = team.vacancies
    if team.captain_id == user_id:
        kb.button(text="Изменить", callback_data=f"edit_vacancy_{vacancy_id}")
        kb.button(text="Удалить", callback_data=f"delete_{vacancy_id}")
    kb.button(text="<<", callback_data=f"vacancies_{team.id}_{offset - 1}")
    kb.button(
        text=">>",
        callback_data=f"vacancies_{team.id}_{(offset + 1) % len(vacancies)}"
    )
    kb.button(text="Назад", callback_data=f"team_{team_id}")
    kb.adjust(2)
    return kb.as_markup(), vacancies[offset]


def vacancies_keyboard(
        user_id: int, team: dtos.Team, page: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    total = len(team.members)
    vac = team.vacancies[page - 1]

    next_page = page + 1 if page <= total else 1
    prev_page = page - 1 if page > 1 else total
    adjust = []
    if user_id == team.captain_id:
        kb.button(text="Изменить роль",
                  callback_data=f"|change_vac_role_{vac.id}")
        kb.button(
            text="Изменить стек технологий",
            callback_data=f"|change_vac_techs_{vac.id}"
        )

        kb.button(
            text="Изменить описание",
            callback_data=f"|change_vac_description_{vac.id}"
        )
        kb.button(text="Удалить", callback_data=f"|delete_vac_{vac.id}")
        adjust += [1, 1, 1, 1]

    kb.button(text="<<", callback_data=f"|team_vacancies_{prev_page}")
    kb.button(text=">>", callback_data=f"|team_vacancies_{next_page}")
    kb.button(text="Назад", callback_data=f"team_{team.id}")
    adjust += [2, 1]
    kb.adjust(*adjust)
    return kb.as_markup()


def technologies_keyboard(techs, cb) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=cb)
    kb.button(text="Добавить автоматически",
              callback_data="add_technology_auto")

    for i, t in enumerate(techs):
        kb.button(text=f"удалить {i + 1})",
                  callback_data=f"delete_technology_{t.id}")

    kb.adjust(1, 1, *[2 for _ in range(len(techs))])
    return kb.as_markup()


def hacks_keyboard(
        hacks: list,
        user_hacks: list[int],
        total: int,
        page: int,
        back: str,
        done: str,
        delete_old_hacks: str,
        limit: int = 5,
) -> InlineKeyboardMarkup:
    # 1 <= len(hacks) <= 5
    kb = InlineKeyboardBuilder()

    for h in hacks:
        txt = h.title
        if h.id in user_hacks:
            txt += "✅"
        kb.button(text=txt, callback_data=f"edit_hack_{page}_{h.id}")

    next_page = page + 1 if page * limit < total else 1
    prev_page = page - 1 if page != 1 else ceil(total / limit)

    kb.button(text="<<", callback_data=f"hacks_pages_{prev_page}")
    kb.button(text=">>", callback_data=f"hacks_pages_{next_page}")
    kb.button(text="Назад", callback_data=back)
    kb.button(text="Готово", callback_data=done)

    if delete_old_hacks:
        kb.button(text="Удалить прошедшие хакатоны",
                  callback_data=delete_old_hacks)

    kb.adjust(*[1 for _ in range(len(hacks))], 2, 2, 2)
    return kb.as_markup()


def edit_team_keyboard(team_id: int):
    kb = InlineKeyboardBuilder()

    kb.button(text="Редактировать название",
              callback_data=f"title_team_edit_{team_id}")
    kb.button(
        text="Редактировать описание",
        callback_data=f"description_team_edit_{team_id}"
    )
    kb.button(
        text="Редактировать желаемые хакатоны",
        callback_data=f"hacks_team_edit_{team_id}",
    )
    kb.button(text="Назад", callback_data=f"team_{team_id}")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()


def go_back(back):
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=back)
    return kb.as_markup()


def invite_keyboard(user_id: int, team_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text="Отклонить", callback_data=f"reject_form")
    kb.button(text="Принять", callback_data=f"approve_form_{team_id}_{user_id}")
    kb.adjust(2)

    return kb.as_markup()


def choose_team(teams) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for t in teams:
        kb.button(text=t["title"], callback_data=f"||invite_to_team_{t['id']}")
    kb.button(text="Назад", callback_data="||cancel")
    kb.adjust(*[1 for _ in range(len(teams) + 1)])
    return kb.as_markup()


def choose_vacancy(vacs) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i in range(len(vacs)):
        kb.button(text=f"{i})", callback_data=f"||invite_to_vac_{vacs[i].id}")
    kb.button(text="Назад", callback_data="||cancel")
    kb.adjust(*[1 for _ in range(len(vacs) + 1)])
    return kb.as_markup()


def accept_invite(team_id: int, vac_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text="Принять",
              callback_data=f"|||accept_invite_{vac_id}_{team_id}")
    kb.button(text="Отклонить", callback_data="||cancel")
    kb.adjust(2)
    return kb.as_markup()
