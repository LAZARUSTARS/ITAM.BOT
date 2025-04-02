import typing as tp
from aiogram import types
from aiogram.utils.i18n import I18nMiddleware

from repositories.users.models import TelegramUser


class Localization(I18nMiddleware):
    async def get_locale(
        self, event: types.TelegramObject, data: tp.Dict[str, tp.Any]
    ) -> str:

        if "tg_user" in data.keys():
            user: TelegramUser = data["tg_user"]
            return user.language_code
        return "ru"
