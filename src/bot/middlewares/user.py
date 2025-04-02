import typing as tp
from aiogram import BaseMiddleware
from aiogram import types


from repositories.users import UserRepositoryBase

# from repositories.coworking import CoworkingRepositoryBase


class UserMiddleware(BaseMiddleware):
    """
    Middleware для обработки пользователей.
    
    Обеспечивает:
    - Автоматическое сохранение информации о пользователях
    - Предоставление доступа к репозиторию пользователей
    - Управление профилями пользователей в обработчиках
    
    Attributes:
        user_repo: Репозиторий для работы с пользователями
    """
    
    def __init__(self, user_repo: UserRepositoryBase) -> None:
        """
        Инициализация middleware.
        
        Args:
            user_repo: Репозиторий для работы с пользователями
        """
        self.user_repo = user_repo

    async def __call__(
        self,
        handler: tp.Callable[
            [types.TelegramObject, tp.Dict[str, tp.Any]], tp.Awaitable[tp.Any]
        ],
        event: types.TelegramObject,
        data: tp.Dict[str, tp.Any],
    ) -> tp.Any:
        """
        Обработка каждого запроса.
        
        Сохраняет информацию о пользователе и добавляет в data:
        - user_repo: Репозиторий пользователей
        - tg_user: Профиль пользователя из базы данных
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Объект события Telegram
            data: Данные для передачи между обработчиками
            
        Returns:
            Результат выполнения следующего обработчика
        """
        aiogram_user: tp.Optional[types.User] = data.get("event_from_user")
        if aiogram_user is None:
            return await handler(event, data)
        self.user_repo.save_user(
            aiogram_user.id,
            aiogram_user.first_name,
            aiogram_user.last_name,
            aiogram_user.username,
        )
        data["user_repo"] = self.user_repo
        data["tg_user"] = (
            self.user_repo.get_user(aiogram_user.id, True) if aiogram_user else None
        ) # TODO: check if we need to get profile all the time

        result = await handler(event, data)

        return result
