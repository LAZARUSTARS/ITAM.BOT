import typing as tp
from aiogram import BaseMiddleware
from aiogram import types
from controllers.club import ClubController

from repositories.users import UserRepositoryBase
from repositories.club import ClubRepositoryBase

class ClubMiddleware(BaseMiddleware):
    def __init__(
        self, user_repo: UserRepositoryBase, club_repo: ClubRepositoryBase
    ) -> None:
        self.user_repo = user_repo
        self.club_repo = club_repo
        self.controller = ClubController(
            club_repo=self.club_repo, user_repo=self.user_repo
        )

    async def __call__(
        self,
        handler: tp.Callable[
            [types.TelegramObject, tp.Dict[str, tp.Any]], tp.Awaitable[tp.Any]
        ],
        event: types.TelegramObject,
        data: tp.Dict[str, tp.Any],
    ) -> tp.Any:

        data["club_controller"] = self.controller

        result = await handler(event, data)

        return result