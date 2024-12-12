from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import inject, Provide

from core.models import vacancy
from core.services import TechnologiesService
from core.repositories import RolesRepository, TechnologiesRepository
from other.states import VacancyForm, VacancyEditForm
from handlers.start import teams

import logging

from core import dtos
from core.dependencies.container import Container
from core.services import VacanciesService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('create_vacancy_'))
@inject
async def create_vacancy(cb: CallbackQuery, state: FSMContext, bot: Bot,
                         db=Provide[Container.db]):
    await state.update_data(team_id=int(cb.data.split('_')[-1]))

    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=cb.from_user.id,
        question="Выберите искомую роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=False,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id,
                            role_message_id=poll_message.message_id)
    await state.set_state(VacancyForm.roles)


@router.poll_answer(VacancyForm.roles)
async def process_roles(poll_answer: PollAnswer, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                                   message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]
        await state.update_data(roles=roles)
        logger.info(f"Roles selected: {roles}")
    await bot.send_message(
        text='Введите описание вакансии',
        chat_id=poll_answer.user.id,
    )
    await state.set_state(VacancyForm.description)


@router.message(F.text, VacancyForm.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply(text='Введите стек, которым должен владеть участник:')
    await state.set_state(VacancyForm.stack)


@router.message(F.text, VacancyForm.stack)
@inject
async def process_stack(message: Message, state: FSMContext,
                        db=Provide[Container.db]):
    txt = message.text.split(',')
    data = await state.get_data()
    seen = set()
    async with db.session() as session:
        vacancy_service = VacanciesService(session)
        tech_repo = TechnologiesRepository(session)
        role_repo = RolesRepository(session)
        for t in txt:
            found = await tech_repo.search_technologies(t.strip())
            if found:
                seen.add(found[0].id)
        if not seen:
            await message.reply('Технологии не найдены, попробуйте снова')
            return
        roles = await role_repo.get_roles_ids(data['roles'])
        vacancy = dtos.CreateVacancy(
            description=data['description'],
            team_id=data['team_id'],
            role_id=roles[0],
            technologies=list(seen)
        )
        await vacancy_service.create_vacancy(vacancy)
        await message.reply(f'Вакансия успешно создана!')
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data=f'team_{data['team_id']}',
        chat_instance=str(message.chat.id)
    )
    await state.clear()
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('|delete_vac_'))
@inject
async def delete_vacancy(cb: CallbackQuery, state: FSMContext,
                         db=Provide[Container.db]):
    vac_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        vac_repo = VacanciesService(session)
        vac = await vac_repo.get_vacancy(vac_id)
        await vac_repo.remove_vacancy(vac_id)
        await cb.message.answer(
            text='Вакансия удалена'
        )
    fake_callback = CallbackQuery(
        id='fake',
        from_user=cb.from_user,
        message=cb.message,
        data=f'team_{vac.team_id}',
        chat_instance=cb.chat_instance
    )
    await state.clear()
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('|change_vac_role_'))
@inject
async def edit_vac_role(cb: CallbackQuery, state: FSMContext, bot: Bot,
                        db=Provide[Container.db]):
    vac_id = int(cb.data.split('_')[-1])
    await state.update_data(vac_id=vac_id)
    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=cb.from_user.id,
        question="Выберите искомую роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=False,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id,
                            role_message_id=poll_message.message_id)
    await state.set_state(VacancyEditForm.roles)


@router.poll_answer(VacancyEditForm.roles)
@inject
async def edit_vac_role_confirm(poll_answer: PollAnswer, state: FSMContext,
                                bot: Bot, db=Provide[Container.db]):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    roles = []
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                                   message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]
        await state.update_data(roles=roles)
        logger.info(f"Roles selected: {roles}")
    await state.clear()

    async with db.session() as session:
        role_repo = RolesRepository(session)
        vac_service = VacanciesService(session)

        roles = await role_repo.get_roles_ids(roles)
        await vac_service.edit_vacancy(
            user_data.get('vac_id'), dtos.CreateVacancy(
                description='', role_id=roles[0], team_id=-1, technologies=[]
            ))
    await bot.send_message(
        text='Вакансия успешно изменена!',
        chat_id=poll_answer.user.id,
    )


@router.callback_query(F.data.startswith('|change_vac_description_'))
async def edit_vac_description(cb: CallbackQuery, state: FSMContext):
    vac_id = int(cb.data.split('_')[-1])
    await state.set_state(VacancyEditForm.description)
    await state.update_data(vac_id=vac_id)
    await cb.message.answer('Отправьте описание вакансии:')


@router.message(F.text, VacancyEditForm.description)
@inject
async def edit_vac_description_confirm(message: Message, state: FSMContext, db=Provide[Container.db]):
    vac_id = (await state.get_data()).get('vac_id')
    desc = message.text
    async with db.session() as session:
        vac_repo = VacanciesService(session)
        vac = await vac_repo.edit_vacancy(vac_id, dtos.CreateVacancy(
            description=desc, team_id=-1, technologies=[], role_id=0
        ))

    await state.clear()
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data=f'teams_{vac.team_id}',
        chat_instance=str(message.chat.id)
    )
    await teams(fake_callback, state)


@router.callback_query(F.data.startswith('|change_vac_techs_'))
async def edit_vac_techs(cb: CallbackQuery, state: FSMContext):
    vac_id = int(cb.data.split('_')[-1])
    await state.update_data(vac_id=vac_id)
    await state.set_state(VacancyEditForm.stack)
    await cb.message.answer(
        text='Введите требуемый стек технологий через запятую:'
    )


@router.message(F.text, VacancyEditForm.stack)
@inject
async def edit_vac_techs_confirm(message: Message, state: FSMContext,
                        db=Provide[Container.db]):
    txt = message.text.split(',')
    data = await state.get_data()
    vac_id = data.get('vac_id')
    seen = set()
    async with db.session() as session:
        vacancy_service = VacanciesService(session)
        tech_repo = TechnologiesRepository(session)
        for t in txt:
            found = await tech_repo.search_technologies(t.strip())
            if found:
                seen.add(found[0].id)
        if not seen:
            await message.reply('Технологии не найдены, попробуйте снова')
            return
        vac = await vacancy_service.edit_vacancy(
            vac_id,
            dtos.CreateVacancy(
                technologies=list(seen), description='', role_id=0, team_id=0
        ))
        await message.answer(f'Вакансия успешно изменена!')
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data=f'team_{vac.team_id}',
        chat_instance=str(message.chat.id)
    )
    await state.clear()
    await teams(fake_callback, state)
