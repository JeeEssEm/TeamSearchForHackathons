import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.config import Config, load_config
from handlers import user_handlers
from keyboards.set_menu import set_main_menu


logger = logging.getLogger(__name__)


async def run_bot():
    """
    Основная функция для запуска Telegram-бота.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s',
    )

    logger.info('Запуск Telegram-бота')

    # Загружаем конфигурацию
    config: Config = load_config()

    # Создаем экземпляры бота и диспетчера
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем обработчики
    dp.include_router(user_handlers.router)

    # Устанавливаем главное меню
    await set_main_menu(bot)

    # Удаляем вебхуки и начинаем опрос
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
