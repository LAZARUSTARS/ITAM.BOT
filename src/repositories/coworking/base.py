import typing as tp
import datetime as dt
from .models import CoworkingStatus
from abc import ABC, abstractmethod


class CoworkingRepositoryBase(ABC):
    @abstractmethod
    def get_status(
        self,
    ) -> CoworkingStatus | None:
        """Получение текущего статуса коворкинга

        CoworkingStatus | None:
            статус коворкинга
        """
        raise NotImplementedError

    @abstractmethod
    def set_status(self, tg_id: int, status: str, duration: int | None = None) -> None:
        """Сохранение нового статуса коворкинга

        Args:
            tg_id (int): id телеграмма, пользователя изменившего статус
            status (str): новый статус коворкинга
            duration (int | None, optional): опциональное поле для временного закрытия коворкинга

        """
        raise NotImplementedError

    @abstractmethod
    def set_coworking_notifications(self, tg_id: int, subscribed: bool) -> None:
        """Обновляет статус подписки на уведомления об изменении статуса коворкинга

        Args:
            tg_id (int): id телеграмма, пользователя изменявшего статус подписки
            subscribed (bool): новый статус подписки на уведомления
        """
        raise NotImplementedError

    @abstractmethod
    def get_coworking_notifications(self, tg_id: int) -> bool:
        """Проверяет подписал ли пользователь на уведомления об изменении статуса коворкинга"""
        raise NotImplementedError

    @abstractmethod
    def get_coworking_subscribed(self) -> list[int]:
        """Получение пользователей подписанных на уведомления об изменении статуса коворкинга

        Returns:
            list[int]: id подписанных пользователей
        """
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, tg_id: int) -> None:

        raise NotImplementedError
