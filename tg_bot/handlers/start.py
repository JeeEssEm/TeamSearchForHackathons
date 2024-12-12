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
from other.search_delegates import (
    get_vacancies_delegate, retrieve_vacancies_delegate,
    get_forms_delegate, retrieve_forms_delegate
)

from core.dependencies.container import Container
from core.services import TeamsService, UsersService
from core.repositories import WishesRepository
from core import dtos

from tg_bot.keyboards.inline_keyboards import vacancies_keyboard

router = Router()

@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    await message.answer('Вы в главном меню',
                         reply_markup=create_main_keyboard())
    await state.clear()

@router.callback_query(F.data == 'start')
async def start_callback(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await cb.message.answer(text ='Вы в главном меню' ,reply_markup=create_main_keyboard())


@router.callback_query(F.data == 'start')
async def cb_start(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await cb.message.delete()
    await state.clear()
    await bot.send_message(
        text='Приветствую тебя в <b>главном меню</b> выбери, что ты хочешь сделать',
        reply_markup=create_main_keyboard(),
        chat_id=cb.message.chat.id
    )


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
    await cb.message.delete()
    team_id = int(cb.data.split('_')[1])
    async with db.session() as session:
        team_service = TeamsService(session)
        team = await team_service.get_team_by_id(team_id)

        team_members = make_msg_list(list([f'{m.name} {m.surname}'
                                           for m in team.members]))
        hacks = make_msg_list(make_hacks_list(team.hacks))
        await cb.message.answer(
            text=f'''Вот твоя команда:
Название команды: {team.title}\n
Описание: {team.description}\n
Состав:\n{team_members}\n
Желаемые хакатоны:\n{hacks}\n
''',
            reply_markup=await my_team_keyboard(cb.from_user.id, team.id),
            parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data.startswith('members_'))
@inject
async def members(cb: CallbackQuery, state: FSMContext):
    team_id, offset = int(cb.data.split('_')[1]), int(cb.data.split('_')[2]) if len(
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


@router.callback_query(F.data.startswith('vacancies_'))
@inject
async def get_vacancies(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    team_id = int(cb.data.split('_')[-1])
    async with db.session() as session:
        team_service = TeamsService(session)
        team = await team_service.get_team_by_id(team_id)
    await state.update_data(team=team)
    await team_vacancies(cb, state)


@router.callback_query(F.data.startswith('|team_vacancies_'))
async def team_vacancies(cb: CallbackQuery, state: FSMContext):
    page = int(cb.data.split('_')[-1]) if 'team' in cb.data else 1
    team = (await state.get_data()).get('team')
    if not team.vacancies:
        await cb.message.answer(
            text='В команде ещё нет вакансий'
        )
        return

    await cb.message.answer(
        text=f'{team.vacancies[page - 1]}',
        reply_markup=vacancies_keyboard(
            user_id=cb.from_user.id,
            team=team,
            page=page,
        )
    )
    await cb.message.delete()


@router.callback_query(F.data == 'search_team')
async def search_team(cb: CallbackQuery, state: FSMContext):
    await state.update_data(
        return_back='start',
        find='init_search',
        delegate=get_vacancies_delegate,
        retrieve_delegate=retrieve_vacancies_delegate
    )
    await set_filters(cb, state)


@router.callback_query(F.data == 'search_form')
async def search_forms(cb: CallbackQuery, state: FSMContext):
    await state.update_data(
        return_back='start',
        find='init_search',
        delegate=get_forms_delegate,
        retrieve_delegate=retrieve_forms_delegate
    )
    await set_filters(cb, state)
