import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dependency_injector.wiring import Provide, inject

from config.config import Config, load_config

from core.dependencies.container import Container

from handlers import (
    create_team, create_vacancy, start, reg, technologies, roles,
    hackathons, edit_team, filters, search_form, invites
)
from handlers.edit_form import (
    name, surname, middlename, uni, group, course, about_me,
)

from keyboards.set_menu import set_main_menu


@inject
async def init_db(db=Provide[Container.db]):
    await db.init_models()


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
    dp.include_router(roles.router)
    dp.include_router(hackathons.router)
    dp.include_router(edit_team.router)
    dp.include_router(filters.router)
    dp.include_router(search_form.router)

    dp.include_router(invites.router)

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
        'handlers.create_vacancy',
        'handlers.technologies',
        'handlers.roles',
        'handlers.hackathons',
        'handlers.edit_team',
        'handlers.filters',
        'other.search_delegates',
        'handlers.invites'
    ])

    # await init_db()
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
