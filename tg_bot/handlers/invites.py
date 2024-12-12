from aiogram import Router, F, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.services import TeamsService, UsersService
from core.repositories import VacanciesRepository, UsersRepository, \
    TeamsRepository
from core.models import FormStatus
from core import dtos

from handlers.edit_form.name import (
    my_forms_handler, make_hacks_list, make_msg_list
)
from handlers.filters import set_filters
from keyboards.inline_keyboards import (
    create_main_keyboard, my_teams_keyboard, my_team_keyboard,
    team_users_keyboard, invite_keyboard, choose_team, choose_vacancy,
    accept_invite
)
from other.states import LeaveFeedbackForm


router = Router()


def build_application_message(vac, team, user) -> str:
    user_stack = make_msg_list(list(map(lambda t: t.title, user.technologies)))
    user_roles = make_msg_list(list(map(lambda r: r.title, user.roles)))

    vac_stack = make_msg_list(list(map(lambda t: t.title, vac.technologies)))
    vac_role = make_msg_list([vac.role])

    hacks = make_msg_list(make_hacks_list(user.hackathons))
    fullname = f'{user.name} {user.middle_name} {user.surname}'

    msg = f'''
В вашу команду <i>{team.title}</i> поступила новая заявка
на вакансию:
<b><i>Роль</i></b>
{vac_role}
<b><i>Технологии</i></b>
{vac_stack}
<b><i>Хакатоны</i></b>

\n
-----------------\n\n
<i><b>ФИО</b></i>
╰{fullname.strip() or '<i>не указано</i>'}
<i><b>Университет</b></i>
╰{user.uni or '<i>не указан</i>'}
<i><b>Курс</b></i>
╰{user.year_of_study or '<i>не указан</i>'}
<i><b>Учебная группа</b></i>
╰{user.group or '<i>не указан</i>'}
<i><b>Информация о себе</b></i>\n
<i>{user.about_me or '<i>не указано</i>'}</i>\n\n
<i><b>Стек технологий</b></i>
{user_stack or '<i>не указано</i>'}
<i><b>Роли</b></i>
{user_roles or '<i>не указано</i>'}
<i><b>Желаемые хакатоны</b></i>
{hacks or '<i>не указано</i>'}
\n
'''

    return msg


@router.callback_query(F.data.startswith('send_application_'))
@inject
async def send_application_handler(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    vac_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        vac_repo = VacanciesRepository(session)
        user_repo = UsersRepository(session)
        teams_service = TeamsService(session)

        current_user = await user_repo.get_user_by_id(cb.from_user.id)
        if current_user.form_status != FormStatus.approved:
            await bot.send_message(
                text='Вы не можете подавать заявку в команду, пока ваша '
                     'анкета не была одобрена модератором',
                chat_id=cb.from_user.id,
            )
            return
        vac = await vac_repo.get_by_id(vac_id)
        team = await teams_service.get_team_by_id(vac.team_id)

        await bot.send_message(
            text=build_application_message(
                vac=vac, team=team, user=current_user
            ),
            reply_markup=invite_keyboard(
                user_id=current_user.id, team_id=team.id),
            chat_id=team.captain_id,
        )
        await cb.message.answer('Вы отправили заявку на вступление в команду')


@router.callback_query(F.data == 'reject_form')
async def reject_form(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith('approve_form_'))
@inject
async def accept_form(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    await cb.message.edit_reply_markup(reply_markup=None)
    team_id = int(cb.data.split('_')[-2])
    user_id = int(cb.data.split('_')[-1])
    async with db.session() as session:
        team_repo = TeamsRepository(session)
        vac_repo = VacanciesRepository(session)
        vac = await vac_repo.get_by_id(team_id)
        await team_repo.add_user_to_team(
            team_id=team_id, user_id=user_id, role_id=vac.role_id
        )

    await cb.message.answer(text='Вы добавили пользователя в команду!')
    await cb.message.delete()
    await bot.send_message(
        text='Вас добавили в команду!',
        chat_id=user_id,
    )


@router.callback_query(F.data == '||cancel')
async def cancel(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()


@router.callback_query(F.data.startswith('send_invite_'))
@inject
async def send_invite_handler(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    receiver_id = int(cb.data.split('_')[-1])
    await state.update_data(receiver_id=receiver_id)
    async with db.session() as session:
        user_service = UsersRepository(session)
        user_teams = await user_service.get_teams(cb.from_user.id)

        if not user_teams:
            await cb.message.answer(
                text='Вы не можете пригласить пользователя в команду, т.к. вы'
                     'не являетесь капитаном ни одной команды'
            )
            return
        await cb.message.answer(
            text='Вы какую команду вы хотите пригласить пользователя?',
            reply_markup=choose_team(user_teams)
        )


@router.callback_query(F.data.startswith('||invite_to_team_'))
@inject
async def invite_to_vacancy(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])
    async with db.session() as session:
        team_repo = TeamsRepository(session)
        team = await team_repo.get_by_id(team_id)
        if not team.vacancies:
            await cb.message.answer('Вы не можете пригласить пользователя'
                                    ' в эту команду, т.к. в ней нет вакансий')
            return
        msg = 'Вакансии в команде'
        for i, vac in enumerate(team.vacancies):
            techs = [t.title for t in vac.technologies]
            msg += f'''
{i}) <b>{vac.role}</b>: <i>{', '.join(techs)}</i>
            '''
        await cb.message.answer(
            text=msg,
            reply_markup=choose_vacancy(team.vacancies),
            parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data.startswith('||invite_to_vac_'))
@inject
async def invite_to_team_confirm(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    await cb.message.delete()
    data = await state.get_data()
    receiver_id = data.get('receiver_id')
    vac_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        team_repo = TeamsRepository(session)
        vac_repo = VacanciesRepository(session)

        vac = await vac_repo.get_by_id(vac_id)
        team = await team_repo.get_by_id(vac.team_id)
        techs = [t.title for t in vac.technologies]
        msg = f'''
Вас пригласили в команду <i>{team.title}</i>
Описание команды:
<i>{team.description}</i>\n

<i><b>Позиция:</b></i>
{vac.role}: {', '.join(techs)}
Описание:
{vac.description}
'''
    await bot.send_message(
        text=msg,
        reply_markup=accept_invite(team.id, vac_id),
        chat_id=receiver_id,
        parse_mode=ParseMode.HTML
    )
    await state.clear()
    await cb.message.answer('Вы отправили приглашение в команду')
    await cb.message.delete()


@router.callback_query(F.data.startswith('|||accept_invite_'))
@inject
async def accept_invite_confirm(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])
    vac_id = int(cb.data.split('_')[-2])

    async with db.session() as session:
        team_repo = TeamsRepository(session)
        vac_repo = VacanciesRepository(session)
        user_repo = UsersRepository(session)
        user = await user_repo.get_baseuser_by_id(cb.from_user.id)
        team = await team_repo.get_by_id(team_id)
        vac = await vac_repo.get_by_id(vac_id)

        await team_repo.add_user_to_team(
            team_id=team_id,
            role_id=vac.role_id,
            user_id=cb.from_user.id
        )

        await cb.message.delete()
        await cb.message.answer('Добро пожаловать в команду!')

        await bot.send_message(
            text=f'{user.name} {user.surname} присоединился к вашей команде'
                 f' {team.title}',
            chat_id=team.captain_id,
        )


@router.callback_query(F.data.startswith('leave_team_'))
@inject
async def leave_team(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])
    async with db.session() as session:
        team_service = TeamsService(session)
        await team_service.kick(team_id=team_id, user_id=cb.from_user.id)
    await cb.message.answer('Вы покинули команду...')
    await cb.message.delete()
