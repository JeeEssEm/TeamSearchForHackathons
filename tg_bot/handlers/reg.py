from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PollAnswer, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from dependency_injector.wiring import Provide, inject

from core.dependencies.container import Container
from core.repositories import TechnologiesRepository, RolesRepository
from core.services.users import UsersService
from core import dtos

from config.config import BaseUser
from handlers.start import start
from handlers.technologies import my_technologies
from handlers.edit_form.name import make_msg_list
from handlers.hackathons import hacks_pages
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import yes_no_kb
from keyboards.inline_keyboards import (
    alphabet_kb, choose_technologies, technologies_keyboard, create_main_keyboard
)
import logging

from other.filters import IsReg
from other.states import UserForm, TechnologyForm
import emoji
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
router.message.filter(~IsReg())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    await state.update_data(user_id=user_id)
    await message.reply(
        "Привет!" + emoji.emojize(":wave:") + "Давай заполним данные для пользователя. Введи свою фамилию"
    )
    await state.set_state(UserForm.last_name)


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
    await message.reply("Введи название своего университета:" + emoji.emojize(":school:"))
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
    await message.reply('❗️ Введите натуральное число' + emoji.emojize(":x:"))


@router.message(F.text, UserForm.group)
@inject
async def process_group(message: Message, state: FSMContext, bot: Bot,
                        db=Provide[Container.db]):
    await state.update_data(group=message.text)
    await message.reply("Теперь выбери свою роль:")

    async with db.session() as session:
        repo = RolesRepository(session)
        roles = await repo.get_all_roles()

    poll_message = await bot.send_poll(
        chat_id=message.chat.id,
        question="Выбери свою роль:",
        options=[role.title for role in roles],
        allows_multiple_answers=True,
        is_anonymous=False
    )
    await state.update_data(role_poll_id=poll_message.poll.id,
                            role_message_id=poll_message.message_id)
    logger.info("Poll for roles sent")
    await state.set_state(UserForm.roles)


@router.poll_answer(UserForm.roles)
async def process_role_poll(poll_answer: PollAnswer, state: FSMContext,
                            bot: Bot):
    user_data = await state.get_data()
    role_poll_id = user_data.get('role_poll_id')
    role_message_id = user_data.get('role_message_id')
    if role_poll_id and role_message_id:
        poll = await bot.stop_poll(chat_id=poll_answer.user.id,
                                   message_id=role_message_id)
        roles = [poll.options[i].text for i in poll_answer.option_ids]
        await state.update_data(roles=roles)
        logger.info(f"Roles selected: {roles}")
    await bot.send_message(
        text='Отлично!' + emoji.emojize(":white_check_mark:") 'Теперь введите ваш стек технологий'
             ' (каждую технологию через запятую)',
        chat_id=poll_answer.user.id)
    logger.info("User data sent")
    await state.set_state(UserForm.technologies)
    # await state.update_data(selected_technologies = [])
    # await bot.send_message(chat_id=poll_answer.user.id, text='Теперь выбери свой стек технологий:',reply_markup=alphabet_kb())


@router.message(F.text, UserForm.technologies)
@inject
async def process_technologies(message: Message, state: FSMContext,
                               db=Provide[Container.db]):
    txt = message.text.split(',')
    res = {}
    seen = set()
    if not txt:
        await message.answer('Введите технологии через запятую...')
        return
    pointer = 0
    msg = []
    async with db.session() as session:
        repo = TechnologiesRepository(session)
        for i, q in enumerate(txt):
            techs = await repo.search_technologies(q)
            t = techs[0] if techs else None
            msg.append(f"{i + 1}) {t.title if t else '<i>не найдено</i>'}")
            if not t or t.id not in seen:
                res[pointer] = None
                pointer += 1
                if t:
                    seen.add(t.id)
    resp_text = f"Вот список ваших технологий:\n{'\n'.join(msg)}"
    await message.reply(
        f'{resp_text}\n\n'
        f'Вы сможете изменить этот список после окончания регистрации\n'
        f'Теперь отправьте вашу аватарку:' + emoji.emojize(":camera:")
    )
    await state.update_data(technologies=seen)
    await state.set_state(UserForm.avatar)


@router.callback_query(F.data == 'continue_avatar')
async def continue_avatar(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(text='Отлично! Теперь отправьте аватар:' + emoji.emojize(":camera:"),
                           chat_id=cb.message.chat.id)
    await state.set_state(UserForm.avatar)


@router.message(F.photo, UserForm.avatar)
async def process_avatar(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(avatar=message.photo[0].file_id)
    await bot.send_message(chat_id=message.chat.id,
                           text='Расскажите немного о себе:')
    await state.set_state(UserForm.about_me)


@router.message(F.text, UserForm.about_me)
async def process_about(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(about_me=message.text, back='complete_hacks',
                            done='complete_hacks', new_message=True)
    await bot.send_message(
        text='Теперь перечислите хакатоны, для которых вы хотите найти команду:',
        chat_id=message.chat.id
    )

    fake_callback = CallbackQuery(
        id='fake',
        from_user=message.from_user,
        message=message,
        data='hacks_pages_1',
        chat_instance=str(message.chat.id)
    )
    await hacks_pages(fake_callback, state)

    # await state.set_state(UserForm.achievements)


@router.callback_query(F.data == 'complete_hacks')
@inject
async def complete_hacks(cb: CallbackQuery, state: FSMContext, bot: Bot,
                         db=Provide[Container.db]):
    await cb.message.delete()
    user_data = await state.get_data()
    techs = list(user_data.get('technologies', []))
    hacks = list(user_data.get('user_hacks', []))
    async with db.session() as session:
        user_service = UsersService(session)
        repo = RolesRepository(session)

        roles = user_data.get('roles')

        user = dtos.CreateUser(
            telegram_id=cb.from_user.id,
            name=user_data.get('first_name'),
            middlename=user_data.get('middle_name'),
            surname=user_data.get('last_name'),
            uni=user_data.get('university'),
            year_of_study=user_data.get('course'),
            group=user_data.get('group'),
            about_me=user_data.get('about_me'),
        )
        user = await user_service.create_user(user)
        if techs:
            await user_service.set_user_technologies(
                user.id, techs
            )
        if roles:
            selected_roles = await repo.get_roles_ids(roles)
            await user_service.set_user_roles(user.id, selected_roles)
        if hacks:
            await user_service.set_user_hacks(user.id, hacks)
    await state.clear()
    await bot.send_message(
        text='Вы в главном меню',
        chat_id=cb.message.chat.id,
        reply_markup=create_main_keyboard()
    )


@router.callback_query(F.data.startswith('technologies_'))
async def _(cb: CallbackQuery, state: FSMContext):
    letter = cb.data[-1]
    data = await state.get_data()
    await cb.message.edit_reply_markup(
        reply_markup=choose_technologies(letter,
                                         data.get('selected_technologies')))
