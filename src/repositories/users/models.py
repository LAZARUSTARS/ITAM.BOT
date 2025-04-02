from dataclasses import dataclass
from pydantic import BaseModel
import typing as tp
from datetime import datetime


class UserProfile(BaseModel):
    fio: str | None = None
    email: str | None = None
    educational_group: str | None = None
    portfolio_link: str | None = None
    majors: list[str] | None = None
    skills: list[str] | None = None
    external_links: list[str] | None = None
    mentor_status: bool | None = None
    company: str | None = None

class AdminRights(BaseModel):
    """Права админа

    Attributes
    ----------
    rights_model: dict[int, str]

    """

    right_model: dict[int, str]


class TelegramUser(BaseModel):
    """Пользователь телеграма

    Attributes
    ----------
    tg_id : int
        id пользователя
    first_name : str
        имя пользователя
    last_name : str | None
        фамилия пользователя
    username : str | None
        юзернейм пользователя
    is_premium : bool
        является ли пользователь премиумом
    language_code : str
        код языка пользователя
    is_admin : bool
        является ли пользователь админом
    """

    tg_id: int
    first_name: str
    last_name: str | None
    username: str | None
    is_premium: bool
    language_code: str
    is_admin: bool
    profile: UserProfile = UserProfile()
    timestamp: datetime | None = None
    admin_rights: AdminRights = AdminRights(right_model={})
