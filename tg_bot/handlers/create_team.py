from aiogram import F, Router, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, \
    PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import RolesRepository
from core.services import TeamsService
from core import dtos

from handlers.edit_form.name import make_msg_list
from handlers.hackathons import hacks_pages
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
    await state.set_state(TeamForm.team_achievements)


@router.message(F.text, TeamForm.team_achievements)
async def process_team_achievements(message: Message, state: FSMContext):
    await state.update_data(team_achievements=message.text)
    await message.reply("В каком актуальном хакатоне вы участвуете?")

    await state.update_data(back='start', done='current_hackathon',
                            new_message=True)
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='hacks_pages_1',
        chat_instance=str(message.chat.id)
    )
    await hacks_pages(fake_callback, state)
    await state.set_state(TeamForm.current_hackathon)


@router.callback_query(F.data == 'current_hackathon')
@inject
async def process_team_role(cb: CallbackQuery, state: FSMContext, bot: Bot,
                            db=Provide[Container.db]):
    await cb.message.delete()
    await cb.message.answer("Какая у вас будет роль?")
    await state.set_state(TeamForm.role)

    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=cb.message.chat.id,
        question="Выбери свою роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=False,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id,
                            role_message_id=poll_message.message_id)


@router.poll_answer(TeamForm.role)
@inject
async def process_current_hackathon(poll_answer: PollAnswer, state: FSMContext,
                                    bot: Bot,
                                    db=Provide[Container.db]):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    roles = []
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                                   message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]

    user_data = await state.get_data()
    hacks = user_data.get('user_hacks', [])
    async with db.session() as session:
        role_repo = RolesRepository(session)
        team_service = TeamsService(session)
        team = dtos.CreateTeam(
            captain_id=poll_answer.user.id, title=user_data['team_name'],
            description=user_data['team_description'],
            hacks=hacks
        )
        role = await role_repo.get_roles_ids(roles)
        team = await team_service.create_team(team, role[0])
        hacks = make_msg_list([h.title for h in team.hacks])
        members = make_msg_list([f'{m.name} {m.surname}' for m in team.members])
        msg = f'''
Вот твоя команда:\n
<i><b>Название команды:</b></i>\n
<i>{user_data['team_name']}</i>
{user_data['team_description']}
<i><b>Желаемые хакатоны:</b></i>
{hacks}
Состав:
{members}
'''
    await bot.send_message(
        text=msg,
        reply_markup=await my_team_keyboard(poll_answer.user.id, team.id),
        chat_id=poll_answer.user.id,
        parse_mode=ParseMode.HTML
    )
    await state.clear()
