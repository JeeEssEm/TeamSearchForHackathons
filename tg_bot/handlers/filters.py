from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.poll_answer import PollAnswer
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dependency_injector.wiring import Provide, inject

from core.services import TeamsService, UsersService
from core.dependencies.container import Container
from core.repositories import (
    RolesRepository, TechnologiesRepository, HackathonsRepository
)
from core import dtos

from handlers.edit_form.name import make_msg_list, make_hacks_list
from handlers.hackathons import hacks_pages
from other.states import FiltersForm
from keyboards.filters_keyboard import get_filters, drop_techs_keyboard

router = Router()


@inject
async def build_message_with_filters(data, db=Provide[Container.db]) -> str:
    roles = make_msg_list(data.get('roles', []))
    techs = make_msg_list([t.title for t in data.get('techs', [])])

    hacks = data.get('user_hacks', [])
    if hacks:
        async with db.session() as session:
            repo = HackathonsRepository(session)
            hacks = await repo.get_hacks_by_ids(hacks)
        hacks = make_msg_list(make_hacks_list(hacks))

    msg = f'''
Текущие фильтры
<b><i>Роли</i></b>
{roles or '<i>не указано</i>'}
<b><i>Технологии</i></b>
{techs or '<i>не указано</i>'}
<b><i>Хакатоны</i></b>
{hacks or '<i>не указано</i>'}
'''
    return msg


@router.callback_query(F.data == 'set_filters')
async def set_filters(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    back = data.get('return_back')
    find = data.get('find')
    # feel_lucky = data.get('find')

    await cb.message.edit_text(
        text=await build_message_with_filters(data)
    )
    await cb.message.edit_reply_markup(
        reply_markup=get_filters(back, find)
    )


@router.callback_query(F.data == 'set_roles')
@inject
async def set_roles(cb: CallbackQuery, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    await cb.message.delete()
    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=cb.message.chat.id,
        question="Выбери роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=True,
        is_anonymous=False
    )
    await state.update_data(role_message_id=poll_message.message_id)
    await state.set_state(FiltersForm.role)


@router.poll_answer(FiltersForm.role)
@inject
async def set_roles_confirm(poll_answer: PollAnswer, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    data = await state.get_data()
    role_message_id = data.get('role_message_id')

    poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                               message_id=role_message_id)
    roles = [poll.options[i].text for i in poll_answer.option_ids]
    await state.update_data(roles=roles)

    back = data.get('return_back')
    find = data.get('find')
    data['roles'] = roles
    # feel_lucky = data.get('find')

    await bot.send_message(
        text=await build_message_with_filters(data),
        reply_markup=get_filters(back, find),
        chat_id=poll_answer.user.id
    )


@router.callback_query(F.data == 'set_techs')
async def set_techs(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.message.delete()

    await bot.send_message(
        text='Введите технологии через запятую:',
        reply_markup=drop_techs_keyboard(),
        chat_id=cb.message.chat.id,
    )
    await state.set_state(FiltersForm.techs)


@router.callback_query(F.data == 'drop_techs')
async def drop_techs(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.message.delete()
    await state.update_data(techs=[])
    data = await state.get_data()
    back = data.get('return_back')
    find = data.get('find')

    await bot.send_message(
        text=await build_message_with_filters(data),
        reply_markup=get_filters(back, find),
        chat_id=cb.message.chat.id
    )


@router.message(F.text, FiltersForm.techs)
@inject
async def set_techs_confirm(message: Message, state: FSMContext, bot: Bot, db=Provide[Container.db]):
    raw = message.text.split(',')
    res = []
    data = await state.get_data()
    async with db.session() as session:
        repo = TechnologiesRepository(session)
        for t in raw:
            techs = await repo.search_technologies(t)
            if techs:
                res.append(techs[0])
    await state.update_data(techs=res)
    data['techs'] = res
    back = data.get('return_back')
    find = data.get('find')

    await bot.send_message(
        text=await build_message_with_filters(data),
        reply_markup=get_filters(back, find),
        chat_id=message.chat.id
    )


@router.callback_query(F.data == 'set_hacks')
async def set_hacks(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()

    await state.update_data(
        back='set_hacks_back',
        done='set_filters',
        new_message=True,
        page=1
    )
    await hacks_pages(cb, state)


@router.callback_query(F.data == 'set_hacks_back')
async def set_hacks_back(cb: CallbackQuery, state: FSMContext):
    await state.update_data(user_hacks=[])
    await set_filters(cb, state)
