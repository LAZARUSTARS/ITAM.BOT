from email import message
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from aiogram.utils.i18n import I18n


from apscheduler.schedulers.asyncio import AsyncIOScheduler

import psycopg2
import dotenv


from .middlewares import (
    UserMiddleware,
    CoworkingMiddleware,
    ClubMiddleware,
    Localization,
    SettingsMiddleware,
    BotMiddleware,
    SchedulerMiddleware,
)


from .handlers import common, coworking, profile, club, itam, broadcast

from repositories.coworking import CoworkingRepositoryPostgres
from repositories.club import ClubRepositoryPostgres
from repositories.users import UserRepositoryPostgres
from .settings import Settings

dotenv.load_dotenv("../.env")


async def main() -> None:
    """
    Основная функция запуска бота.
    
    Инициализирует и настраивает:
    - Подключение к базе данных PostgreSQL
    - Планировщик задач APScheduler
    - Репозитории для работы с данными (пользователи, коворкинг, клуб)
    - Систему локализации i18n
    - Middleware компоненты
    - Обработчики команд
    
    Middleware компоненты:
    - SettingsMiddleware: Управление настройками бота
    - BotMiddleware: Основной функционал бота
    - UserMiddleware: Управление пользователями
    - CoworkingMiddleware: Управление коворкинг-пространством
    - ClubMiddleware: Управление клубом
    - SchedulerMiddleware: Управление запланированными задачами
    
    Returns:
        None
    """
    settings = Settings()  # type: ignore
    print(settings.build_postgres_dsn())
    pg_connection = psycopg2.connect(settings.build_postgres_dsn())

    scheduler = AsyncIOScheduler()

    user_repo = UserRepositoryPostgres(pg_connection)
    coworking_repo = CoworkingRepositoryPostgres(pg_connection)
    club_repo = ClubRepositoryPostgres(pg_connection)
    i18n = I18n(path="translations", default_locale="ru", domain="messages")

    bot = Bot(settings.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    locale = Localization(i18n)
    locale.setup(dp)

    dp.update.outer_middleware(SettingsMiddleware(settings))
    dp.update.outer_middleware(BotMiddleware(bot))
    dp.update.outer_middleware(UserMiddleware(user_repo))

    dp.update.middleware(CoworkingMiddleware(user_repo, coworking_repo))
    dp.update.middleware(ClubMiddleware(user_repo, club_repo))
    dp.update.middleware(SchedulerMiddleware(scheduler))
    dp.include_routers(common.router, coworking.router, profile.router, club.router, itam.router, broadcast.router)

    admins = user_repo.get_admins()
    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        pg_connection.close()
        scheduler.shutdown()
        await bot.session.close()
        sys.exit(0)
