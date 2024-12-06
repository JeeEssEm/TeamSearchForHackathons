from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PollAnswer, CallbackQuery
from aiogram.fsm.context import FSMContext

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.services.users import UsersService
from core import dtos

from config.config import BaseUser
from handlers.start import start
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import yes_no_kb
from keyboards.inline_keyboards import alphabet_kb, choose_technologies
import logging

from other.filters import IsReg
from other.states import UserForm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
router.message.filter(~IsReg())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    await state.update_data(user_id=user_id)
    await message.reply("Привет! Давай заполним данные для пользователя")
    await state.set_state(UserForm.last_name)


# @router.message(F.text, UserForm.email)
# async def process_email(message: Message, state: FSMContext):
#     await state.update_data(email=message.text)
#     await message.reply("Введи свою фамилию:")
#     await state.set_state(UserForm.last_name)


@router.message(F.text, UserForm.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.reply("Введи свое имя:")
    await state.set_state(UserForm.first_name)


@router.message(F.text, UserForm.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.reply("Введи свое отчество:")
    await state.set_state(UserForm.middle_name)


@router.message(F.text, UserForm.middle_name)
async def process_middle_name(message: Message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    await message.reply("Введи название своего университета:")
    await state.set_state(UserForm.university)


@router.message(F.text, UserForm.university)
async def process_university(message: Message, state: FSMContext):
    await state.update_data(university=message.text)
    await message.reply("Введи свой курс (число):")
    await state.set_state(UserForm.course)


@router.message(F.text, UserForm.course)
async def process_course(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(course=int(message.text))
        await message.reply("Введи свою группу:")
        await state.set_state(UserForm.group)
        return
    await message.reply('❗️ Введите натуральное число')


@router.message(F.text, UserForm.group)
async def process_group(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(group=message.text)
    await message.reply("Теперь выбери свою роль:")
    poll_message = await bot.send_poll(
        chat_id=message.chat.id,
        question="Выбери свою роль:",
        options=["Frontend", "Backend", "ML"],  # FIXME: refactor to ids from db
        allows_multiple_answers=True,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id, role_message_id=poll_message.message_id)
    logger.info("Poll for roles sent")
    await state.set_state(UserForm.roles)


@router.poll_answer(UserForm.roles)
async def process_role_poll(poll_answer: PollAnswer, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id, message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]
        await state.update_data(roles=roles)
        logger.info(f"Roles selected: {roles}")
    await bot.send_message(text='Отлично! Теперь отправьте аватар:', chat_id=poll_answer.user.id)
    logger.info("User data sent")
    await state.set_state(UserForm.avatar)
    # await state.update_data(selected_technologies = [])
    # await bot.send_message(chat_id=poll_answer.user.id, text='Теперь выбери свой стек технологий:',reply_markup=alphabet_kb())


@router.message(F.photo, UserForm.avatar)
async def process_avatar(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(avatar=message.photo[0].file_id)
    await bot.send_message(chat_id=message.chat.id, text='Расскажите немного о себе:')
    await state.set_state(UserForm.about_me)


@router.message(F.text, UserForm.about_me)
async def process_about(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(about_me=message.text)
    await bot.send_message(text='Теперь перечислите выигранные вами хакатоны:', chat_id=message.chat.id)
    await state.set_state(UserForm.achievements)


@router.message(F.text, UserForm.achievements)
@inject
async def process_achievements(message: Message, state: FSMContext, bot: Bot,
                               db=Provide[Container.db]):
    await state.update_data(achievements=message.text)
    user_data = await state.get_data()
    async with db.session() as session:
        user_service = UsersService(session)
        user = dtos.CreateUser(
            telegram_id=message.from_user.id,
            name=user_data.get('first_name'),
            middlename=user_data.get('middle_name'),
            surname=user_data.get('last_name'),
            uni=user_data.get('university'),
            year_of_study=user_data.get('course'),
            group=user_data.get('group'),
            about_me=user_data.get('about_me'),
        )  # TODO: сделать добавление ролей в телеге
        await user_service.create_user(user)
    await start(message=message, state=state)


@router.callback_query(F.data.startswith('technologies_'))
async def _(cb: CallbackQuery, state: FSMContext):
    letter = cb.data[-1]
    data = await state.get_data()
    await cb.message.edit_reply_markup(reply_markup=choose_technologies(letter, data.get('selected_technologies')))
