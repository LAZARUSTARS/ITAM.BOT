import typing as tp
import datetime as dt
from abc import ABC, abstractmethod
from .models import ClubInfo

class ClubRepositoryBase(ABC):

    @abstractmethod
    def get_club_info(self, club: str) -> ClubInfo | None:
        """Получение информации о клубе

        Args:
            club (str): название клуба

        Returns:
            ClubInfo: информация о клубе
        """
        raise NotImplementedError

    @abstractmethod
    def set_club_notifications(self, tg_id: int, subscribed: bool, club: str) -> None:
        """Обновляет статус подписки на уведомления отт клуба

        Args:
            tg_id (int): id телеграмма, пользователя изменявшего статус подписки
            subscribed (bool): новый статус подписки на уведомления
            club (str): клуб, на который подписывается пользователь
        """
        raise NotImplementedError

    @abstractmethod
    def get_club_notifications(self, tg_id: int, club: str) -> bool:
        """Проверяет подписал ли пользователь на уведомления от клуба"""
        raise NotImplementedError

    @abstractmethod
    def get_club_subscribed(self, club: str) -> list[int]:
        """Получение пользователей подписанных на уведомления от клуба

        Returns:
            list[int]: id подписанных пользователей
        """
        raise NotImplementedError