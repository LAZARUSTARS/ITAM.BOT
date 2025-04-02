import typing as tp
from aiogram import BaseMiddleware, types, Bot


class BotMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def __call__(
        self,
        handler: tp.Callable[
            [types.TelegramObject, tp.Dict[str, tp.Any]], tp.Awaitable[tp.Any]
        ],
        event: types.TelegramObject,
        data: tp.Dict[str, tp.Any],
    ) -> tp.Any:

        data["bot"] = self.bot
        result = await handler(event, data)

        return result
