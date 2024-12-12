from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from dependency_injector.wiring import Provide, inject

from keyboards.search_keyboards import (
    search_vacancy_keyboard, search_form_keyboard)

from core.dependencies.container import Container
from core.repositories import (
    VacanciesRepository, RolesRepository, UsersRepository
)


@inject
async def get_vacancies_delegate(state: FSMContext, user_id: int, db=Provide[Container.db]):
    data = await state.get_data()
    techs = [t.id for t in data.get('techs', [])]
    hacks = data.get('user_hacks', [])
    roles = data.get('roles', [])

    async with db.session() as session:
        vac_repo = VacanciesRepository(session)
        role_repo = RolesRepository(session)
        user_repo = UsersRepository(session)
        user_teams = [t['id'] for t in await user_repo.get_teams(user_id)]
        roles_ids = await role_repo.get_roles_ids(roles)

        vacs = await vac_repo.search_vacancies(
            hacks=hacks, techs=techs, roles=roles_ids, user_teams=user_teams
        )
    await state.update_data(vacancies=vacs)


async def retrieve_vacancies_delegate(state: FSMContext, page: int) -> (str, InlineKeyboardMarkup):
    data = await state.get_data()
    vacs = data.get('vacancies')

    if not vacs:
        return
    current = vacs[page - 1]

    msg = f'{current}'
    return msg, search_vacancy_keyboard(len(vacs), page, current.id)


@inject
async def get_forms_delegate(state: FSMContext, user_id: int, db=Provide[Container.db]):
    data = await state.get_data()
    techs = [t.id for t in data.get('techs', [])]
    hacks = data.get('user_hacks', [])
    roles = data.get('roles', [])

    async with db.session() as session:
        role_repo = RolesRepository(session)
        user_repo = UsersRepository(session)
        roles_ids = await role_repo.get_roles_ids(roles)

        forms = await user_repo.search_users(
            hacks=hacks, techs=techs, roles=roles_ids,
            user_id=user_id
        )
    await state.update_data(forms=forms)


async def retrieve_forms_delegate(state: FSMContext, page: int) -> (str, InlineKeyboardMarkup):
    data = await state.get_data()
    vacs = data.get('forms')

    if not vacs:
        return
    current = vacs[page - 1]
    msg = f'{current.name}'
    return msg, search_form_keyboard(len(vacs), page, current.id)
