from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import Provide, inject

from keyboards.inline_keyboards import my_form_edit_field_keyboard
from other.states import UserEditForm
from .name import my_forms_handler

from core.dependencies.container import Container
from core.services import UsersService
from core import dtos
import emoji
router = Router()


@router.callback_query(F.data == 'my_form_edit_uni')
async def my_form_edit_uni(cb: CallbackQuery, state: FSMContext):
    await cb.message.reply('Окей, введи свой <b>университет</b>' + emoji.emojize(":school:"),
                           reply_markup=my_form_edit_field_keyboard(
                               'my_forms', 'my_form_delete_uni'
                           ),
                           parse_mode=ParseMode.HTML)
    await state.set_state(UserEditForm.university)
    await cb.message.delete()


@router.callback_query(F.data == 'my_form_delete_uni')
@inject
async def my_form_delete_uni(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        await service.update_user(
            cb.from_user.id,
            dtos.UpdateUser(uni='')
        )
    await cb.message.answer('Университет успешно изменён!' + emoji.emojize(":white_check_mark:"))
    fake_callback = CallbackQuery(
        id='fake',
        from_user=cb.from_user,
        message=cb.message,
        data='my_forms',
        chat_instance=cb.chat_instance
    )
    await my_forms_handler(fake_callback, state)


@router.message(F.text, UserEditForm.university)
@inject
async def process_edit_uni(message: Message, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        await service.update_user(
            message.from_user.id,
            dtos.UpdateUser(uni=message.text.strip())
        )
    await message.answer('Университет успешно изменён!' + emoji.emojize(":white_check_mark:"))
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='my_forms',
        chat_instance=str(message.chat.id)
    )
    await my_forms_handler(fake_callback, state)

