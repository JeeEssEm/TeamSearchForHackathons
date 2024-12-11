from aiogram import F, Router, Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PollAnswer, CallbackQuery
from aiogram.fsm.context import FSMContext

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import TechnologiesRepository
from core.services.users import UsersService
from core import dtos

from config.config import BaseUser
from handlers.start import start
from handlers.edit_form.name import make_msg_list
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import yes_no_kb
from keyboards.inline_keyboards import alphabet_kb, choose_technologies, \
    technologies_keyboard
import logging

from other.filters import IsReg
from other.states import UserForm, TechnologyForm
import emoji
router = Router()


@router.callback_query(F.data == 'my_technologies')
@inject
async def my_technologies(cb: CallbackQuery, state: FSMContext,
                          db=Provide[Container.db]):
    await cb.message.delete()
    async with db.session() as session:
        service = UsersService(session)
        user = await service.get_user(cb.from_user.id)

    msg = []
    for i, t in enumerate(user.technologies):
        msg.append(
            f"{i + 1}) {t.title if t else '<i>не найдено</i>'}")

    resp_text = f"Вот список ваших технологий:\n{'\n'.join(msg)}"
    await cb.message.answer(
        resp_text, parse_mode=ParseMode.HTML,
        reply_markup=technologies_keyboard(
            user.technologies,
            cb='my_forms')
    )


@router.callback_query(F.data.startswith('add_technology_manually'))
async def add_technology_manually(cb: CallbackQuery, state: FSMContext):
    position = int(cb.data.split('_')[-1])  # какую технологию из списка меняем
    await cb.message.delete()
    await cb.message.answer(
        text='Выбери букву, с которой начинается технология:',
        reply_markup=alphabet_kb(position)  # FIXME: how to go back?
    )


@router.callback_query(F.data.startswith('delete_technology_'))
@inject
async def delete_technology(cb: CallbackQuery, state: FSMContext,
                            db=Provide[Container.db]):
    tech_id = int(cb.data.split('_')[-1])

    async with db.session() as session:
        service = UsersService(session)
        await service.delete_user_technology(cb.from_user.id, tech_id)
    await cb.message.answer(text='Технология успешно удалена!' + emoji.emojize(":white_check_mark:"))
    await my_technologies(cb, state)


@router.callback_query(F.data == 'add_technology_auto')
async def add_technology_auto(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.set_state(TechnologyForm.selected_technologies)
    await cb.message.answer('Введите название вашей технологии')


@router.message(F.text, TechnologyForm.selected_technologies)
@inject
async def process_add_technology_auto(message: Message, state: FSMContext,
                                      db=Provide[Container.db]):
    tech = message.text
    async with db.session() as session:
        user_service = UsersService(session)
        tech_repo = TechnologiesRepository(session)

        found = await tech_repo.search_technologies(tech)
        if found:
            user = await user_service.get_user(message.from_user.id)
            if found[0] in user.technologies:
                await message.answer('Технология уже есть в вашем списке!')
            else:
                await user_service.set_user_technologies(message.from_user.id,
                                                         [found[0].id])
                await message.answer('Технология успешно добавлена!'emoji.emojize(":white_check_mark:") + )
        else:
            await message.answer('Технология не найдена' + emoji.emojize(":x:"))
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='my_forms',
        chat_instance=str(message.chat.id)
    )
    await my_technologies(fake_callback, state)
    await state.clear()
