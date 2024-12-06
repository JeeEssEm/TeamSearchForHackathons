from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.services import TeamsService
from core import dtos
from keyboards.inline_keyboards import my_team_keyboard
from other.states import TeamForm

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'new_team')
async def cmd_create_team(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Создаем команду! Укажите название команды:")
    await state.set_state(TeamForm.team_name)


@router.message(F.text, TeamForm.team_name)
async def process_team_name(message: Message, state: FSMContext):
    await state.update_data(team_name=message.text)
    await message.reply("Отлично! Расскажите немного о команде:")
    await state.set_state(TeamForm.team_description)


@router.message(F.text, TeamForm.team_description)
async def process_team_description(message: Message, state: FSMContext):
    await state.update_data(team_description=message.text)
    await message.reply("Пришлите фото для аватара вашей команды:")
    await state.set_state(TeamForm.avatar)


@router.message(F.photo, TeamForm.avatar)
async def process_avatar(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(avatar=message.photo[0].file_id)
    await bot.send_message(chat_id=message.chat.id, text='Какие достижения у вашей команды?')
    await state.set_state(TeamForm.team_achievements)


@router.message(F.text, TeamForm.team_achievements)
async def process_team_achievements(message: Message, state: FSMContext):
    await state.update_data(team_achievements=message.text)
    await message.reply("В каком актуальном хакатоне вы участвуете?")
    await state.set_state(TeamForm.current_hackathon)


@router.message(F.text, TeamForm.current_hackathon)
async def process_team_role(message: Message, state: FSMContext):
    await state.update_data(current_hackathon=message.text)
    await message.reply("Какая у вас будет роль?")
    await state.set_state(TeamForm.role)


@router.message(F.text, TeamForm.role)
@inject
async def process_current_hackathon(message: Message, state: FSMContext,
                                    db=Provide[Container.db]):
    await state.update_data(role=message.text)
    user_data = await state.get_data()
    async with db.session() as session:
        team_service = TeamsService(session)
        team = dtos.CreateTeam(
            captain_id=message.from_user.id, title=user_data['team_name'],
            description=user_data['team_description'],
            hacks=[],  # FIXME: добавлять не один хакатон, а пачку. Fuzzy Search
            # current_hackathon=user_data['current_hackathon'],
            # achievements=user_data['team_achievements'],
            # avatar=user_data['avatar']
        )

        team = await team_service.create_team(team, 1)
        # FIXME: сделать выбор для роли капитана в команде
        # team = await Team(captain_id=message.from_user.id, title=user_data['team_name'],
    #                   description=user_data['team_description'], avatar=user_data['avatar'],
    #                   current_hackathon=user_data['current_hackathon'], achievements=user_data['team_achievements']).save()
    # await TeamUsers(message.from_user.id, 1, team.id).save()

    await message.answer_photo(photo=user_data['avatar'], caption=f'''Вот твоя команда:
Название команды: {user_data['team_name']}
{user_data['team_description']}''', reply_markup=await my_team_keyboard(message.from_user.id, team.id))
    await state.clear()
