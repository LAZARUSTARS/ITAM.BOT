from abc import ABC, abstractmethod
from .models import TelegramUser, AdminRights
from datetime import datetime


class UserRepositoryBase(ABC):
    @abstractmethod
    def get_user(
        self, tg_id: int, include_profile: bool = False
    ) -> TelegramUser | None:
        """Получение данных пользователя

        Args:
            tg_id (int): id пользователя в телеграм
            include_profile (bool, optional): флаг, для получение данных профиля


        Returns:
            TelegramUser | None: Данные пользователя
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_admin_rights(self, tg_id: int) -> AdminRights | None:
        """Получение прав администратора пользователя

        Args:
            tg_id (int): id пользователя в телеграме

        Returns:
            AdminRights | None: права администратора
        """
        raise NotImplementedError

    @abstractmethod
    def get_users(self, limit: int = 10, offset: int = 0) -> list[TelegramUser]:
        """Получения информации пользователей для сбора статистики"""
        raise NotImplementedError

    @abstractmethod
    def get_users_after_timestamp(self, timestamp_bound: datetime) -> list[TelegramUser]:
        """Получение пользователей, которые были зарегестрированы после опредленной даты/времени"""
        raise NotImplementedError

    @abstractmethod
    def save_user(
        self,
        tg_id: int,
        first_name: str,
        last_name: str | None,
        username: str | None,
        is_premium: bool = False,
        language_code: str = "ru",
    ) -> None:
        """Сохранение данных пользователя из телеграма

        используется для определения language_code, хранения информации о правах доступа

        Args:
            tg_id (int): id пользователя в телеграме
            first_name (str): имя пользователя
            last_name (str | None): фамилия пользователя
            username (str | None): имя профиля в телеграме
            is_premium (bool, optional): является ли пользователь премиумом. Defaults to False.
            language_code (str, optional): код языка пользователя из телеграма. Defaults to "ru".


        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def is_admin(self, tg_id: int) -> bool:
        """Получение статуса пользователя"""
        raise NotImplementedError

    @abstractmethod
    def get_admins(self) -> list[int]:
        """Получение списка администраторов, для уведомлений

        Returns:
            list[int]: список id администраторов
        """
        raise NotImplementedError

    @abstractmethod
    def create_invite_code(self, code: str, admin_id: int, rights_ids: list) -> None:
        """Сохранение кода для активации получения прав администратора

        Args:
            code (str): код для активации прав администратора
            admin_id (int): id создателя кода
            rights_ids (list): лист id прав администратора
        """
        raise NotImplementedError

    @abstractmethod
    def use_invite_code(self, code: str, user_id: int) -> None:
        """Активация пригласительного кода
        гарантирует, что код можно использовать только один раз иначе кидает


        Raises:
            Exception(f"Code already activated by {used_by}") used_by - id пользователя, кто активировал код
        иначе фиксирует время активации кода и id пользователя, который его активировал

        Args:
            code (str): код для активации прав администратора
            user_id (int): id пользователя который активирует код
        """
        raise NotImplementedError

    @abstractmethod
    def save_profile_data(
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
        company: str | None = None,
    ) -> None:
        """Обновления дополнительной ифнормации профиля"""
        raise NotImplementedError

    def get_broadcast_users(self, auditory: str) -> list[int]:
        """Получение списка подписчиков для рассылки"""
        raise NotImplementedError