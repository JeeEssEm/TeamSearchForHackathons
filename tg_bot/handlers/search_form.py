from aiogram import Router, F, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.services import TeamsService, UsersService
from core.repositories import WishesRepository
from core import dtos

from handlers.edit_form.name import (
    my_forms_handler, make_hacks_list, make_msg_list
)
from handlers.filters import set_filters
from keyboards.inline_keyboards import (
    create_main_keyboard, my_teams_keyboard, my_team_keyboard,
    team_users_keyboard
)
from other.states import LeaveFeedbackForm


router = Router()


@router.callback_query(F.data == 'init_search')
async def search_init(cb: CallbackQuery, state: FSMContext, bot: Bot):
    # await cb.message.delete()
    data = await state.get_data()
    delegate = data.get('delegate')

    await delegate(state, cb.from_user.id)
    await search(cb, state, bot, new_msg=True)


@router.callback_query(F.data.startswith('search_'))
async def search(cb: CallbackQuery, state: FSMContext, bot: Bot, new_msg: bool = False):
    page = int(cb.data.split('_')[-1]) if cb.data.startswith('search_') else 1
    data = await state.get_data()
    retriever = data.get('retrieve_delegate')

    res = await retriever(state, page)
    if not res:
        # await cb.message.delete()
        await bot.send_message(
            text='Ничего не найдено',
            chat_id=cb.message.chat.id,
        )
        await set_filters(cb, state)
        return

    if new_msg:
        await bot.send_message(
            text=res[0], reply_markup=res[1],
            chat_id=cb.message.chat.id,
        )
        return

    await cb.message.edit_text(res[0])
    await cb.message.edit_reply_markup(reply_markup=res[1])
