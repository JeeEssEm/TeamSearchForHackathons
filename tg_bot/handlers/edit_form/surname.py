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


@router.callback_query(F.data == 'my_form_edit_surname')
async def my_form_edit_name(cb: CallbackQuery, state: FSMContext):
    await cb.message.reply('Окей, введи свою <b>фамилию</b>',
                           reply_markup=my_form_edit_field_keyboard(
                               'my_forms', 'my_form_delete_surname'
                           ),
                           parse_mode=ParseMode.HTML)
    await state.set_state(UserEditForm.last_name)
    await cb.message.delete()


@router.callback_query(F.data == 'my_form_delete_surname')
@inject
async def my_form_delete_name(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        await service.update_user(
            cb.from_user.id,
            dtos.UpdateUser(surname='')
        )
    await cb.message.answer('Фамилия успешно изменена!' + emoji.emojize(":white_check_mark:"))
    fake_callback = CallbackQuery(
        id='fake',
        from_user=cb.from_user,
        message=cb.message,
        data='my_forms',
        chat_instance=cb.chat_instance
    )
    await my_forms_handler(fake_callback, state)


@router.message(F.text, UserEditForm.last_name)
@inject
async def process_edit_name(message: Message, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        await service.update_user(
            message.from_user.id,
            dtos.UpdateUser(surname=message.text.strip())
        )
    await message.answer('Фамилия успешно изменена!' + emoji.emojize(":white_check_mark:"))
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='my_forms',
        chat_instance=str(message.chat.id)
    )
    await my_forms_handler(fake_callback, state)

