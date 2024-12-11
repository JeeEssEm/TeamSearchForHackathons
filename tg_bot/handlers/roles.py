from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PollAnswer, CallbackQuery, Chat
from aiogram.fsm.context import FSMContext

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import TechnologiesRepository, RolesRepository
from core.services.users import UsersService

from config.config import BaseUser
from handlers.edit_form.name import my_forms_handler
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import yes_no_kb
from keyboards.inline_keyboards import (
    alphabet_kb, choose_technologies, technologies_keyboard
)
from other.states import RoleForm
import emoji
router = Router()


@router.callback_query(F.data == 'edit_roles')
@inject
async def edit_roles(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    await state.set_state(RoleForm.roles)

    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=cb.message.chat.id,
        question="Выбери свою роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=True,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id, role_message_id=poll_message.message_id)


@router.poll_answer(RoleForm.roles)
@inject
async def set_roles(poll_answer: PollAnswer, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                                   message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]
        async with db.session() as session:
            user_service = UsersService(session)
            repo = RolesRepository(session)
            selected_roles = await repo.get_roles_ids(roles)
            await user_service.delete_user_roles(poll_answer.user.id)
            await user_service.set_user_roles(poll_answer.user.id,
                                              selected_roles)
    await bot.send_message(
        text='Роли успешно изменены!' + emoji.emojize(":white_check_mark:"),
        chat_id=poll_answer.user.id
    )
    await state.clear()
