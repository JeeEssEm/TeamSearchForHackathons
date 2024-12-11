from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from other.states import VacancyForm

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


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
async def process_stack(message: Message, state: FSMContext):
    await state.update_data(stack=message.text)
    data = await state.get_data()
    ...





