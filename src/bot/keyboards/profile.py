"""
1. Возможность редактировать следующие параметры:
    1. ФИО
    2. Ник в telegram
    3. Корпоративная почта МИСИС (в домене @edu.misis.ru)
    4. Учебная группа
    5. Ссылка на GitHub репозиторий
    6. Направление — frontend, backend и т д
    7. Навыки — стек технологий в рамках направления
    8. Ссылки — гит, резюме и прочие
    9. Готовность помогать новичкам — готов/не готов
    10. в какой компании работает

Подумать насчет экспортом в гугл докс
И как это хранить в бд?)
"""


import datetime as dt
import typing as tp
from aiogram import types


from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

from ..keyboards.menu import MainMenuCallback

# TODO move into enums
PROFILE_ACTIONS = tp.Literal["user_form", "editing", "admin_menu", "save"]


ADMIN_PROFILE_ACTIONS = tp.Literal["export", "change_status", "add_admin"]
PROFILE_EDITABLE_FIELD = tp.Literal[
    "fio",
    "email",
    "educational_group",
    "portfolio_link",
    "majors",
    "skills",
    "external_links",
    "mentor_status",
    "company",
]


# AVALIABLE_PROFESSIONS = [
#     "Fullstack",
#     "Backend",
#     "Frontend",
#     "GameDev",
#     "Mobile",
#     "DevOps",
#     "ML Engineer",
#     "UI/UX Designer",
#     "Project Manager",
# ]

AVALIABLE_PROFESSIONS = {
    "Flstk": "Fullstack",
    "Bd": "Backend",
    "Fd": "Frontend",
    "Gdv": "GameDev",
    "Mob": "Mobile",
    "DO": "DevOps",
    "ML": "ML Engineer",
    "UI": "UI/UX Designer",
    "CD": "Communication Design",
    "PM":"Project Manager",
}


class ProfileMenuCallback(CallbackData, prefix="profile"):
    """
    Данные которые можно изменить через меню профиля
    1. ФИО
    2. Ник в telegram +
    3. Корпоративная почта МИСИС (в домене @edu.misis.ru)
    4. Учебная группа
    5. Ссылка на GitHub репозиторий опционально?
    6. Направление — frontend, backend и т д
    7. Навыки — стек технологий в рамках направления
    8. Ссылки — гит, резюме и прочие
    9. Готовность помогать новичкам — готов/не готов
    10. в какой компании работает

    # fio: str | None = None
    # email: str | None = None
    # educational_group: str | None = None
    # portfolio_link: str | None = None
    # majors: list[str] | None = None
    # skills: list[str] | None = None
    # external_links: list[str] | None = None
    # mentor_status: bool | None = None
    # company: str | None = None
    """

    action: PROFILE_ACTIONS | None = None
    field: PROFILE_EDITABLE_FIELD | None = None


class MajorCallback(CallbackData, prefix="pf_mj"):
    value: str | None = None
    confirms: str | None = None

class MentorStatusCallback(CallbackData, prefix="mentor_status"):
    ready: bool | None = None


class ProfileAdminMenuCallback(CallbackData, prefix="profile_admin"):
    action: ADMIN_PROFILE_ACTIONS

class AddAdminCallback(CallbackData, prefix="add_admin"):
    value: str | None = None
    confirms: str | None = None

def profile_menu_keyboard(is_admin: bool = False) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=_("🤷‍♂️ Изменить данные"),
            callback_data=ProfileMenuCallback(action="user_form").pack(),
        ),
    )

    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=MainMenuCallback(next_menu_prefix="menu").pack(),
        ),
    )
    if is_admin:
        builder.row(
            types.InlineKeyboardButton(
                text=_("🦺 Меню администратора"),
                callback_data=ProfileMenuCallback(action="admin_menu").pack(),
            )
        )

    return builder.as_markup()


def field_selector_menu() -> types.InlineKeyboardMarkup:
    # FIXME: flexible fields for editing
    builder = InlineKeyboardBuilder()
    callback_data = ProfileMenuCallback(action="editing").pack()
    builder.row(
        types.InlineKeyboardButton(
            text=_("ФИО"),
            callback_data=ProfileMenuCallback(action="editing", field="fio").pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Почта @edu.misis.ru"),
            callback_data=ProfileMenuCallback(action="editing", field="email").pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Учебная группа"),
            callback_data=ProfileMenuCallback(
                action="editing", field="educational_group"
            ).pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Ссылка на портфолио"),
            callback_data=ProfileMenuCallback(
                action="editing", field="portfolio_link"
            ).pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Направления разработки"),
            callback_data=ProfileMenuCallback(action="editing", field="majors").pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Навыки/Стэк технологий"),
            callback_data=ProfileMenuCallback(action="editing", field="skills").pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Ссылки на соц. сети"),
            callback_data=ProfileMenuCallback(
                action="editing", field="external_links"
            ).pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Менторство"),
            callback_data=ProfileMenuCallback(
                action="editing", field="mentor_status"
            ).pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Компания"),
            callback_data=ProfileMenuCallback(action="editing", field="company").pack(),
        ),
    )

    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=ProfileMenuCallback(action=None).pack(),
        )
    )

    return builder.as_markup()


def editing_keyboard(next_input: bool = False) -> types.InlineKeyboardMarkup:
    """
    next_input: flag for adding next value
    """
    builder = InlineKeyboardBuilder()
    if next_input:
        pass
        # builder.row(types.InlineKeyboardButton(text=_("Добавить еще значение")))
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=ProfileMenuCallback(action="user_form").pack(),
        )
    )
    return builder.as_markup()


def majors_keyboard(confirms: str = '') -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, major in AVALIABLE_PROFESSIONS.items():
        text = f"✅ {major}" if key in confirms else major
        value = f"add_{key}" if key not in confirms else f"rm_{key}"
        builder.row(
            types.InlineKeyboardButton(
                text=text, callback_data=MajorCallback(value=value, confirms=confirms).pack()
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=ProfileMenuCallback(action="user_form").pack(),
        )
    )
    if confirms:
        builder.add(
            types.InlineKeyboardButton(
                text=_("Подтвердить"),
                callback_data=MajorCallback(value="save", confirms=confirms).pack(),
            )
        )
    return builder.as_markup()

def mentor_status_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=_("✅ Готов помогать"),
            callback_data=MentorStatusCallback(ready=True).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("❌ Не готов помогать"),
            callback_data=MentorStatusCallback(ready=False).pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=ProfileMenuCallback(action="user_form").pack(),
        )
    )
    return builder.as_markup()


def admin_menu_keyboard(is_admin: bool) -> types.InlineKeyboardMarkup:
    """
    2. Администраторский:
    1. Аналогичные пользовательскому
    2. Получить список участников по направлению — выводит список людей по направлению, уровень владения навыками и контакты
    3. Получить профиль пользователя — выводит полную информацию по профилю пользователя
    4. Присвоить пользователю статус — позволяет админу присвоить уровень навыков пользователя. Предполагаемые статусы Intern, Junior, Middle, Senior. Они отображают суммарный уровень владения навыками по направлению
    """
    builder = InlineKeyboardBuilder()
    if is_admin:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Экспортировать"),
                callback_data=ProfileAdminMenuCallback(action="export").pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("Добавить админа"),
            callback_data=ProfileAdminMenuCallback(action="add_admin").pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=MainMenuCallback(next_menu_prefix="profile").pack(),
        )
    )
    return builder.as_markup()

def select_admin_rights_keyboard(admin_options: dict, confirms: str = '') -> types.InlineKeyboardMarkup:
    """
    generate keyboard for selecting admin rights
    """

    builder = InlineKeyboardBuilder()
    for key, right in admin_options.items():
        key = str(key)
        text = f"✅ {right}" if key in confirms else right
        value = f"add_{key}" if key not in confirms else f"rm_{key}"
        builder.row(
            types.InlineKeyboardButton(
                text=text, callback_data=AddAdminCallback(value=value, confirms=confirms).pack()
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=ProfileMenuCallback(action="admin_menu").pack(),
        )
    )
    if confirms:
        builder.add(
            types.InlineKeyboardButton(
                text=_("Подтвердить"),
                callback_data=AddAdminCallback(value="save", confirms=confirms).pack(),
            )
        )
    return builder.as_markup()
