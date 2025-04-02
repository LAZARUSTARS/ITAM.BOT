import typing as tp
from aiogram import BaseMiddleware
from aiogram import types
from ..settings import Settings


class SettingsMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def __call__(
        self,
        handler: tp.Callable[
            [types.TelegramObject, tp.Dict[str, tp.Any]], tp.Awaitable[tp.Any]
        ],
        event: types.TelegramObject,
        data: tp.Dict[str, tp.Any],
    ) -> tp.Any:
        data["settings"] = self.settings
        result = await handler(event, data)

        return result
