from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.services import TeamsService, UsersService
from core.repositories import WishesRepository
from core import dtos

from handlers.edit_form.name import my_forms_handler
from keyboards.inline_keyboards import (
    create_main_keyboard, my_teams_keyboard, my_team_keyboard,
    team_users_keyboard
)
from other.states import LeaveFeedbackForm

router = Router()

@router.message(Command('start'))
@inject
async def start(message: Message, state: FSMContext, db=Provide[Container.db]):
    await db.init_models()
    await message.answer('Вы в главном меню',
                         reply_markup=create_main_keyboard())
    await state.clear()


@router.callback_query(F.data == 'my_teams')
@inject
async def my_teams(cb: CallbackQuery, state: FSMContext,
                   db=Provide[Container.db]):
    await cb.message.answer(text='Выберите команду:',
                            reply_markup=await my_teams_keyboard(
                                cb.from_user.id))
    await cb.message.delete()


@router.callback_query(F.data.startswith('team_'))
@inject
async def teams(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[1])
    async with db.session() as session:
        team_service = TeamsService(session)
        team = await team_service.get_team_by_id(team_id)
        # TODO: добавление хакатонов с fuzzy search по базе
        team_members = ''.join(
            list(map(lambda m: f'\t - _{m.name} {m.surname}_ \n', team.members))
        )
        await cb.message.answer(
            text=f'''Вот твоя команда:
Название команды: {team.title}
Описание: {team.description}
Состав:\n {team_members}''',
            reply_markup=await my_team_keyboard(cb.from_user.id, team.id),
            parse_mode=ParseMode.MARKDOWN
        )
        await cb.message.delete()


@router.callback_query(F.data.startswith('members_'))
@inject
async def members(cb: CallbackQuery, state: FSMContext):
    team_id, offset = cb.data.split('_')[1], int(cb.data.split('_')[2]) if len(
        cb.data.split('_')) > 2 else 0

    kb, user = await team_users_keyboard(cb.from_user.id, team_id, offset)

    await cb.message.answer(text=f'''{user.name} {user.surname}
Роль: {user.role}
Стек: {', '.join(list(map(lambda t: t.title, user.technologies)))}
{user.about_me or '***<Пусто>***'}''',

                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=kb
                            )
    await cb.message.delete()


@router.callback_query(F.data == 'leave_feedback')
async def leave_feedback(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.set_state(LeaveFeedbackForm.feedback)
    await cb.message.answer('Напишите ваш фидбек')


@router.message(F.text, LeaveFeedbackForm.feedback)
@inject
async def leave_feedback_message(message: Message, state: FSMContext, db=Provide[Container.db]):
    await state.clear()
    async with db.session() as session:
        repo = WishesRepository(session)
        await repo.create_wish(dtos.CreateWish(
            user_id=message.from_user.id,
            description=message.text,
        ))
    await message.answer('Спасибо за ваш фидбек!')
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='my_forms',
        chat_instance=str(message.chat.id)
    )
    await my_forms_handler(fake_callback, state)
