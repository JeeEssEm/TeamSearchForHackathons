import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dependency_injector.wiring import Provide, inject

from config.config import Config, load_config

from core.dependencies.container import Container

from handlers import create_team, create_vacancy, start, reg, technologies
from handlers.edit_form import (
    name, surname, middlename, uni, group, course, about_me
)

from keyboards.set_menu import set_main_menu


logger = logging.getLogger(__name__)


@inject
async def init_db(db=Provide[Container.db]):
    await db.init_models()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(reg.router)
    dp.include_router(start.router)
    dp.include_router(create_team.router)
    dp.include_router(create_vacancy.router)

    dp.include_router(name.router)
    dp.include_router(middlename.router)
    dp.include_router(surname.router)
    dp.include_router(group.router)
    dp.include_router(uni.router)
    dp.include_router(course.router)
    dp.include_router(about_me.router)

    dp.include_router(technologies.router)

    container = Container()
    container.wire(modules=[
        __name__,
        'handlers.reg',
        'handlers.create_team',
        'other.filters',
        'keyboards.inline_keyboards',
        'handlers.start',
        'handlers.edit_form.name',
        'handlers.edit_form.surname',
        'handlers.edit_form.middlename',
        'handlers.edit_form.uni',
        'handlers.edit_form.group',
        'handlers.edit_form.course',
        'handlers.edit_form.about_me',
        'handlers.technologies'
    ])

    # await init_db()
    await set_main_menu(bot)
    # logging.disable(logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
