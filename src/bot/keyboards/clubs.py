import typing as tp
from aiogram import types

from .menu import MainMenuCallback
from .broadcast import BroadcastCallback
from repositories.club.models import ClubInfo, ButtonLinks
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

class SubscriptionCallback(CallbackData, prefix="club_subscription"):
    subscribed: bool
    club: str

def club_subscription_and_info(subscribed: bool, club: str, club_link: str, additional_links: tp.List[ButtonLinks], is_admin: bool) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if subscribed:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Отписаться"),
                callback_data=SubscriptionCallback(subscribed=False, club=club).pack(),
            )
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Подписаться"),
                callback_data=SubscriptionCallback(subscribed=True, club=club).pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("📢 Чат клуба"),
            url=club_link
        )
    )
    for additional_link in additional_links:
        builder.row(
            types.InlineKeyboardButton(
                text=additional_link.button_text,
                url=additional_link.link
            )
        )
    if is_admin:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Рассылка для подписчиков 📢"),
                callback_data=BroadcastCallback(action="menu", auditory=club).pack()
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=MainMenuCallback(next_menu_prefix="clubs").pack(),
        )
    )

    return builder.as_markup()