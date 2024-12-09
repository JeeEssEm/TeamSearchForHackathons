from aiogram import F, Router, Bot
from aiogram.dispatcher.dispatcher import Dispatcher
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
from keyboards.inline_keyboards import alphabet_kb, choose_technologies
import logging

from other.filters import IsReg
from other.states import UserForm


router = Router()


@router.callback_query(F.data.startswith('edit_technology_'))
async def edit_technology(cb: CallbackQuery, state: FSMContext):
    ...

