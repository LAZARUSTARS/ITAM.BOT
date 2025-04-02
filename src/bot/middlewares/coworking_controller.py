import typing as tp
from aiogram import BaseMiddleware
from aiogram import types
from controllers.coworking import CoworkingController


from repositories.users import UserRepositoryBase
from repositories.coworking import CoworkingRepositoryBase


class CoworkingMiddleware(BaseMiddleware):
    def __init__(
        self, user_repo: UserRepositoryBase, coworking_repo: CoworkingRepositoryBase
    ) -> None:
        self.user_repo = user_repo
        self.coworking_repo = coworking_repo
        self.controller = CoworkingController(
            user_repo=self.user_repo, coworking_repo=self.coworking_repo
        )

    async def __call__(
        self,
        handler: tp.Callable[
            [types.TelegramObject, tp.Dict[str, tp.Any]], tp.Awaitable[tp.Any]
        ],
        event: types.TelegramObject,
        data: tp.Dict[str, tp.Any],
    ) -> tp.Any:

        data["coworking_controller"] = self.controller

        result = await handler(event, data)

        return result
