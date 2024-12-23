from aiogram import F, Router, Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PollAnswer, CallbackQuery
from aiogram.fsm.context import FSMContext

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import HackathonsRepository, UsersRepository
from core.services.users import UsersService
from core import dtos

from config.config import BaseUser

from handlers.edit_form.name import my_forms_handler

from keyboards.inline_keyboards import (
    alphabet_kb, choose_technologies, technologies_keyboard, hacks_keyboard
)
import logging

from other.filters import IsReg
from other.states import UserForm, TechnologyForm

router = Router()


@router.callback_query(F.data == 'hacks')
@inject
async def hacks_start(cb: CallbackQuery, state: FSMContext,  db=Provide[Container.db]):
    await cb.message.edit_text('Выберите желаемые хакатоны:')
    async with db.session() as session:
        user_service = UsersService(session)

        user = await user_service.get_user(cb.from_user.id)
        await state.update_data(user_hacks=[h.id for h in user.hackathons])
    await state.update_data(
        page=1,
        delete_old_hacks=f'remove_old_hacks_user_{cb.from_user.id}'
    )
    await hacks_pages(cb, state)


@router.callback_query(F.data.startswith('remove_old_hacks_user_'))
@inject
async def remove_old_hacks_user(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    user_id = int(cb.data.split('_')[-1])
    async with db.session() as session:
        repo = UsersRepository(session)
        await repo.remove_old_hacks(user_id)
    await my_forms_handler(cb, state)


@router.callback_query(F.data.startswith('hacks_pages_'))
@inject
async def hacks_pages(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    data = await state.get_data()
    back = data.get('back', 'my_forms')
    done = data.get('done', 'done_hacks')
    new_message = data.get('new_message', False)
    flag = cb.data.startswith('hacks_pages')
    delete_old_hacks = data.get('delete_old_hacks', '')
    page = int(cb.data.split('_')[-1]) if flag else data['page']

    user_hacks = (await state.get_data()).get('user_hacks', [])
    async with db.session() as session:
        hacks_repo = HackathonsRepository(session)
        total, hacks = await hacks_repo.get_list(page, 5, {
            'date': 'future',
            'sort_start_date': 'asc'
        })

    if not new_message:
        await cb.message.edit_reply_markup(
            reply_markup=hacks_keyboard(hacks, user_hacks, total, page,
                                        back, done, delete_old_hacks)
        )
        return
    await state.update_data(new_message=False)
    await cb.message.answer(
        text='Выберите желаемые хакатоны',
        reply_markup=hacks_keyboard(hacks, user_hacks, total, page,
                                    back, done, delete_old_hacks)
    )


@router.callback_query(F.data.startswith('edit_hack_'))
async def edit_hack(cb: CallbackQuery, state: FSMContext):
    user_hacks = (await state.get_data()).get('user_hacks', [])
    page = int(cb.data.split('_')[-2])
    hack_id = int(cb.data.split('_')[-1])

    if hack_id in user_hacks:
        user_hacks.remove(hack_id)
    else:
        user_hacks.append(hack_id)
    await state.update_data(user_hacks=user_hacks)

    await state.update_data(page=page)
    await hacks_pages(cb, state)


@router.callback_query(F.data == 'done_hacks')
@inject
async def done_hacks(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    user_hacks = (await state.get_data()).get('user_hacks', [])
    async with db.session() as session:
        user_service = UsersService(session)
        await user_service.delete_user_hacks(cb.from_user.id)
        if user_hacks:
            await user_service.set_user_hacks(cb.from_user.id, user_hacks)
    await cb.message.answer('Желаемые хакатоны успешно изменены!')
    await state.clear()

    await my_forms_handler(cb, state)
