from datetime import date

from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, \
    PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import RolesRepository, TeamsRepository
from core.services import TeamsService
from core import dtos

from handlers.hackathons import hacks_pages
from handlers.start import teams
from keyboards.inline_keyboards import (
    my_team_keyboard, edit_team_keyboard, go_back
)
from other.states import TeamForm, TeamEditForm

import logging


router = Router()


@router.callback_query(F.data.startswith('edit_team_'))
async def edit_team(cb: CallbackQuery, state: FSMContext):
    team_id = int(cb.data.split('_')[-1])

    await cb.message.edit_reply_markup(
        reply_markup=edit_team_keyboard(team_id)
    )


@router.callback_query(F.data.startswith('title_team_edit_'))
async def edit_team_title(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.message.delete()
    team_id = int(cb.data.split('_')[-1])
    await bot.send_message(
        text='Введи новое название команды:',
        reply_markup=go_back(f'team_{team_id}'),
        chat_id=cb.message.chat.id
    )
    await state.update_data(team_id=team_id)
    await state.set_state(TeamEditForm.team_name)


@router.message(F.text, TeamEditForm.team_name)
@inject
async def edit_team_title_confirm(message: Message, state: FSMContext, db=Provide[Container.db]):
    title = message.text
    team_id = int((await state.get_data()).get('team_id'))
    async with db.session() as session:
        service = TeamsService(session)
        await service.edit_team_by_id(
            team_id,
            dtos.EditTeam(title=title)
        )
    await state.clear()
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data=f'team_{team_id}',
        chat_instance=str(message.chat.id)
    )
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('description_team_edit_'))
async def edit_team_description(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.message.delete()
    team_id = int(cb.data.split('_')[-1])
    await bot.send_message(
        text='Введи новое описание команды:',
        reply_markup=go_back(f'team_{team_id}'),
        chat_id=cb.message.chat.id
    )
    await state.update_data(team_id=team_id)
    await state.set_state(TeamEditForm.team_description)


@router.message(F.text, TeamEditForm.team_description)
@inject
async def edit_team_description_confirm(message: Message, state: FSMContext, db=Provide[Container.db]):
    description = message.text
    team_id = int((await state.get_data()).get('team_id'))
    async with db.session() as session:
        service = TeamsService(session)
        await service.edit_team_by_id(
            team_id,
            dtos.EditTeam(description=description)
        )
    await state.clear()
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data=f'team_{team_id}',
        chat_instance=str(message.chat.id)
    )
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('hacks_team_edit_'))
@inject
async def edit_team_hacks(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        service = TeamsService(session)
        team = await service.get_team_by_id(team_id)

    await state.update_data(
        page=1, back=f'team_{team_id}', done=f'hacks_team_done_{team_id}',
        new_message=True, user_hacks=[h.id for h in team.hacks],
        delete_old_hacks=f'old_hacks_team_delete_{team_id}'
    )
    await hacks_pages(cb, state)


@router.callback_query(F.data.startswith('hacks_team_done_'))
@inject
async def team_done_hacks(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])
    team_hacks = (await state.get_data()).get('user_hacks', [])
    async with db.session() as session:
        repo = TeamsRepository(session)
        await repo.remove_all_hacks(team_id)
        if team_hacks:
            await repo.add_hacks_to_team(team_id, team_hacks)
    await cb.message.answer('Желаемые хакатоны успешно изменены!')
    await state.clear()
    fake_callback = CallbackQuery(
        id='fake',
        from_user=cb.from_user,
        message=cb.message,
        data=f'team_{team_id}',
        chat_instance=cb.chat_instance
    )
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('old_hacks_team_delete_'))
@inject
async def delete_old_team_hacks(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])
    async with db.session() as session:
        repo = TeamsRepository(session)
        await repo.remove_old_hacks(team_id)
    await cb.answer('Устаревшие хакатоны успешно удалены!')
    fake_callback = CallbackQuery(
        id='fake',
        from_user=cb.from_user,
        message=cb.message,
        data=f'team_{team_id}',
        chat_instance=cb.chat_instance
    )
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('change_team_role_'))
@inject
async def change_team_role(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-2])
    user_id = int(cb.data.split('_')[-1])

    await state.set_state(TeamEditForm.role)
    await state.update_data(team_id=team_id, user_id=user_id)

    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=cb.message.chat.id,
        question="Выбери роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=False,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id, role_message_id=poll_message.message_id)


@router.poll_answer(TeamEditForm.role)
@inject
async def edit_role_team_confirm(poll_answer: PollAnswer, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    team_id = user_data.get('team_id')
    user_id = user_data.get('user_id')

    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                                   message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]
        async with db.session() as session:
            service = TeamsService(session)
            repo = RolesRepository(session)
            selected_roles = await repo.get_roles_ids(roles)
            await service.edit_user_role(team_id, user_id,
                                         selected_roles[0])

    await bot.send_message(
        text='Роль успешно изменена!',
        chat_id=poll_answer.user.id
    )
    await state.clear()


@router.callback_query(F.data.startswith('kick_'))
@inject
async def kick(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-2])
    user_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        team_service = TeamsService(session)
        await team_service.kick(team_id=team_id, user_id=user_id)
    await cb.message.answer('Пользователь исключён из команды')
    await cb.message.delete()


@router.callback_query(F.data.startswith('make_captain_'))
@inject
async def make_capitan(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-2])
    user_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        team_service = TeamsService(session)
        await team_service.make_capitan(team_id=team_id, user_id=user_id)
    await cb.message.answer('Пользователь теперь капитан')
    await cb.message.delete()

