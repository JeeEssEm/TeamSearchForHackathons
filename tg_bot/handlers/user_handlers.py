from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PollAnswer, CallbackQuery
from aiogram.fsm.context import FSMContext
from config.config import UserForm, BaseUser
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import yes_no_kb
from keyboards.inline_keyboards import alphabet_kb, choose_technologies
import logging 



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=yes_no_kb)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)  
    await state.update_data(user_id=user_id) 
    await message.reply("Привет! Давай заполним данные для пользователя. Введи свой email:")
    await state.set_state(UserForm.email)

@router.message(F.text, UserForm.email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.reply("Введи свою фамилию:")
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
        options=["Frontend", "Backend", "ML"],
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
    user_data = await state.get_data()

    user = BaseUser(
        user_id=user_data['user_id'],
        email=user_data['email'],
        last_name=user_data['last_name'],
        first_name=user_data['first_name'],
        middle_name=user_data['middle_name'],
        university=user_data['university'],
        course=user_data['course'],
        group=user_data['group'],
        roles=user_data['roles']
    )
    await bot.send_message(chat_id=poll_answer.user.id, text=f"Данные пользователя:\n{user}")
    logger.info("User data sent")
    await state.clear()
    await state.update_data(selected_technologies = [])
    await bot.send_message(chat_id=poll_answer.user.id, text='Тепери выбери свой стек технологий:',reply_markup=alphabet_kb())


@router.callback_query(F.data.startswith('technologies_'))
async def _(cb: CallbackQuery, state: FSMContext):
    letter = cb.data[-1]
    data = await state.get_data()
    await cb.message.edit_reply_markup(reply_markup=choose_technologies(letter, data.get('selected_technologies'))) 