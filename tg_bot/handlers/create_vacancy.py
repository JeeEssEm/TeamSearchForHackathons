from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import inject, Provide
from other.states import VacancyForm

import logging

from core import dtos
from core.dependencies.container import Container
from core.services import VacanciesService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data.startswith('create_vacancy_'))
async def create_vacancy(cb: CallbackQuery, state: FSMContext):
    await state.update_data(team_id = int(cb.data.split('_')[-1]))
    await cb.message.reply('Введите искомую роль:')
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


# @router.message(F.text, VacancyForm.stack)
# @inject
# async def process_stack(message: Message, state: FSMContext,db=Provide[Container.db]):
#     await state.update_data(stack=message.text)
#     data = await state.get_data()
#     async with db.session() as session:
#         vacancy_service = VacanciesService(session)
#         vacancy = dtos.CreateVacancy(description=data['description'],team_id=data['team_id'], role_id=data['role'])
#         vacancy = await vacancy_service.create_vacancy(vacancy)




