from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from dependency_injector.wiring import Provide, inject
from core.dependencies.container import Container
from core.services import TeamsService, UsersService

from keyboards.inline_keyboards import (
    create_main_keyboard, my_teams_keyboard, my_team_keyboard,
    team_users_keyboard
)

router = Router()


@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
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
