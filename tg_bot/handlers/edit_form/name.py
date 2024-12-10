from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dependency_injector.wiring import Provide, inject

from keyboards.inline_keyboards import my_form_keyboard, my_form_edit_field_keyboard
from other.states import UserEditForm

from core.dependencies.container import Container
from core.services import UsersService
from core import dtos
from core.models import FormStatus

router = Router()


def make_msg_list(collection: list) -> str:
    col = [f'├{t}' for t in collection]
    if col:
        col[-1] = '╰' + col[-1][1:]
    return '\n'.join(col)


@router.callback_query(F.data == 'my_forms')
@inject
async def my_forms_handler(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        user = await service.get_user(cb.from_user.id)
        stack = make_msg_list(list(map(lambda t: t.title, user.technologies)))
        roles = make_msg_list(list(map(lambda r: r.title, user.roles)))
        fullname = f'{user.name} {user.middle_name} {user.surname}'
        status = 'в рассмотрении'
        if user.form_status == FormStatus.approved:
            status = 'одобрено'
        elif user.form_status == FormStatus.rejected:
            status = f'отклонено по причине: {user.moderator_feedback or '<i>не указано</i>'}'
        msg = f'''
Вот твоя анкета
<i><b>ФИО</b></i>
╰{fullname.strip() or '<i>не указано</i>'}
<i><b>Университет</b></i>
╰{user.uni or '<i>не указан</i>'}
<i><b>Курс</b></i>
╰{user.year_of_study or '<i>не указан</i>'}
<i><b>Учебная группа</b></i>
╰{user.group or '<i>не указан</i>'}
<i><b>Информация о себе</b></i>\n
<i>{user.about_me or '<i>не указано</i>'}</i>\n\n
<i><b>Стек технологий</b></i>
{stack or '<i>не указано</i>'}
<i><b>Роли</b></i>
{roles or '<i>не указано</i>'}
\n
Статус анкеты: {status}
'''
        await cb.message.answer(msg, parse_mode=ParseMode.HTML,
                                reply_markup=my_form_keyboard())
        await cb.message.delete()


@router.callback_query(F.data == 'my_form_edit_name')
async def my_form_edit_name(cb: CallbackQuery, state: FSMContext):
    await cb.message.reply('Окей, введи своё <b>имя</b>',
                           reply_markup=my_form_edit_field_keyboard(
                               'my_forms', 'my_form_delete_name'
                           ),
                           parse_mode=ParseMode.HTML)
    await state.set_state(UserEditForm.first_name)
    await cb.message.delete()


@router.callback_query(F.data == 'my_form_delete_name')
@inject
async def my_form_delete_name(cb: CallbackQuery, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        await service.update_user(
            cb.from_user.id,
            dtos.UpdateUser(name='')
        )
    await cb.message.answer('Имя успешно изменено!')
    fake_callback = CallbackQuery(
        id='fake',
        from_user=cb.from_user,
        message=cb.message,
        data='my_forms',
        chat_instance=cb.chat_instance
    )
    await my_forms_handler(fake_callback, state)


@router.message(F.text, UserEditForm.first_name)
@inject
async def process_edit_name(message: Message, state: FSMContext, db=Provide[Container.db]):
    async with db.session() as session:
        service = UsersService(session)
        await service.update_user(
            message.from_user.id,
            dtos.UpdateUser(name=message.text.strip())
        )
    await message.answer('Имя успешно изменено!')
    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='my_forms',
        chat_instance=str(message.chat.id)
    )
    await my_forms_handler(fake_callback, state)
