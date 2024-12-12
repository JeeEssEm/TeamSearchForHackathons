from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import inject, Provide
from other.states import VacancyForm

import logging

from sqlalchemy.testing.plugin.plugin_base import options

from core import dtos
from core.dependencies.container import Container
from core.services import VacanciesService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
options = ["Frontend", "Backend", "ML"]
@router.callback_query(F.data.startswith('create_vacancy_'))
async def create_vacancy(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(team_id = int(cb.data.split('_')[-1]))
    poll_message = await bot.send_poll(
        chat_id=cb.from_user.id,
        question="Выберите искомую роль:",
        options=["Frontend", "Backend", "ML"],  # FIXME: refactor to ids from db
        allows_multiple_answers=False,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id, role_message_id=poll_message.message_id)
    await state.set_state(VacancyForm.roles)


@router.poll_answer(VacancyForm.roles)
async def process_roles(poll_answer: PollAnswer, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id, message_id=role_message_id)
        print(poll)
        roles = [poll.options[i].text for i in poll_answer.option_ids][0]
        # roles = options[poll_answer.option_ids[0]]
        await state.update_data(roles=roles)
        logger.info(f"Roles selected: {roles}")
    await bot.send_message(chat_id=poll_answer.user.id, text='Введите описание роли:')

@router.message(Command(commands='create_vacancy'))
async def create_vacancy(message: Message, state: FSMContext):
    await message.reply('Введите искомую роль:')
    await state.set_state(VacancyForm.role)


@router.message(F.text, VacancyForm.role)
async def process_role(message: Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.reply(text='Введите описание роли:')
    await state.set_state(VacancyForm.description)


@router.message(F.text, VacancyForm.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply(text='Введите стек, которым должен владеть участник:')
    await state.set_state(VacancyForm.stack)


@router.message(F.text, VacancyForm.stack)
@inject
async def process_stack(message: Message, state: FSMContext,db=Provide[Container.db]):
    await state.update_data(stack=message.text)
    data = await state.get_data()

    async with db.session() as session:
        vacancy_service = VacanciesService(session)
        vacancy = dtos.CreateVacancy(description=data['description'],team_id=data['team_id'], role_id=str(data['roles']))
        vacancy = await vacancy_service.create_vacancy(vacancy)
        await message.reply(f'''{data['roles']}''')
    await state.clear()
