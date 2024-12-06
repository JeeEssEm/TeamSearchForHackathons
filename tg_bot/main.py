import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.dependencies.container import Container

from handlers import create_team, create_vacancy, start, reg
from config.config import Config, load_config
from keyboards.set_menu import set_main_menu


logger = logging.getLogger(__name__)


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

    container = Container()
    container.wire(modules=[
        'handlers.reg',
        'handlers.create_team',
        'other.filters',
        'keyboards.inline_keyboards',
        'handlers.start'
    ])

    await set_main_menu(bot)
    # logging.disable(logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
