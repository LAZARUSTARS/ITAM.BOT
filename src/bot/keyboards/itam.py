import typing as tp
from aiogram import types

from .menu import MainMenuCallback
from .broadcast import BroadcastCallback
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

DIGEST_ACTIONS = tp.Literal[
    "view", "subscribe", "unsubscribe", "admin_menu"
]

class DigestMenuCallback(CallbackData, prefix="digest"):
    action: DIGEST_ACTIONS

class ITAMMenuCallback(CallbackData, prefix="itam"):
    action: str

def itam_menu(in_contacts: bool = False, is_admin: bool = False) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # builder.row(
    #     types.InlineKeyboardButton(
    #         text=_("📰 Дайджест"),
    #         callback_data=DigestMenuCallback(action="view").pack(),
    #     ),
    # )
    builder.row(
        types.InlineKeyboardButton(
            text=_("🚀 Наши возможности"),
            url="https://info.itatmisis.ru/",
        ),
    )
    if in_contacts:
        builder.row(
            types.InlineKeyboardButton(
                text=_("ℹ️ О нас"),
                callback_data=ITAMMenuCallback(action="about").pack(),
            ),
        )
    else:
        builder.row(
        types.InlineKeyboardButton(
            text=_("📞 Контакты"),
            callback_data=ITAMMenuCallback(action="contacts").pack(),
        ),
    )
    if is_admin:
        builder.row(
            types.InlineKeyboardButton(
                text=_("📢 Рассылка всем пользователям"),
                callback_data=BroadcastCallback(action="menu", auditory="all").pack(),
            ),
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=MainMenuCallback(next_menu_prefix="menu").pack(),
        ),
    )

    return builder.as_markup()

def digest_keyborad(subscribed: bool, is_admin: bool = False) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if subscribed:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Отписаться от дайджеста"),
                callback_data=DigestMenuCallback(action="unsubscribe").pack(),
            ),
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Подписаться на дайджест"),
                callback_data=DigestMenuCallback(action="subscribe").pack(),
            ),
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=MainMenuCallback(next_menu_prefix="ITAM").pack(),
        ),
    )
    if is_admin:
        builder.row(
            types.InlineKeyboardButton(
                text=_("🔧 Администрирование"),
                callback_data=DigestMenuCallback(action="admin_menu").pack(),
            ),
        )
    return builder.as_markup()