import typing as tp
from aiogram import types

from .menu import MainMenuCallback
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


class SubscriptionCallback(CallbackData, prefix="coworking_subscription"):
    subscribed: bool


def coworking_subscription(subscribed: bool) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if subscribed:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Отписаться"),
                callback_data=SubscriptionCallback(subscribed=True).pack(),
            )
        )
    else:
        builder.row(
            types.InlineKeyboardButton(
                text=_("Подписаться"),
                callback_data=SubscriptionCallback(subscribed=False).pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=MainMenuCallback(next_menu_prefix="coworking").pack(),
        )
    )

    return builder.as_markup()
