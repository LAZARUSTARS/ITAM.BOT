import datetime as dt

from repositories.coworking import CoworkingRepositoryBase
from repositories.coworking.models import CoworkingStatus
from repositories.users import UserRepositoryBase
from repositories.users.models import TelegramUser, AdminRights


class UserController:
    """
    - изменение данных профиля
    - возможность подписаться и отправить уведомления пользователям
    """

    def __init__(self, user_repo: UserRepositoryBase) -> None:
        self.user_repo = user_repo

    async def save_user(self):
        "save_user"
        raise NotImplementedError

    async def get_users(self, limit: int = 10, offset: int = 0) -> list[TelegramUser]:
        raise NotImplementedError

    async def get_user_admin_rights(self, tg_id: int) -> AdminRights | None:
        raise NotImplementedError

    async def save_profile_data(
        self,
        tg_id: int,
        fio: str | None = None,
        email: str | None = None,
        educational_group: str | None = None,
        portfolio_link: str | None = None,
        majors: list[str] | None = None,
        external_links: list[str] | None = None,
        skills: list[str] | None = None,
        mentor_status: bool = False,
    ) -> None:
        """ """
        raise NotImplementedError

    async def get_user(
        self, tg_id: int, include_profile: bool = False
    ) -> TelegramUser | None:
        raise NotImplementedError

    async def get_broadcast_users(self, auditory: str) -> list[int]:
        raise NotImplementedError

    # async def
