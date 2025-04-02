import typing as tp
from aiogram import types
import datetime as dt

from .menu import MainMenuCallback, ClubsMenuCallback, CoworkingMenuCallback
from repositories.club.models import ClubInfo, ButtonLinks
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _

class BroadcastCallback(CallbackData, prefix="broadcast"):
    action: str
    auditory: str

def broadcast_keyboard(auditory: str, back_callback: CallbackData, scheduled_messages: dict) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if scheduled_messages:
        for key, value in scheduled_messages.items():
            builder.row(
                types.InlineKeyboardButton(
                    text=f"🗑️ Отменить рассылку на {dt.datetime.strftime(value, '%Y-%m-%d %H-%M')} ",
                    callback_data=BroadcastCallback(action=f"cancel_{key}", auditory=auditory).pack()
                )
            )
    builder.row(
        types.InlineKeyboardButton(
            text=_("📢 Отправить сейчас"),
            callback_data=BroadcastCallback(action="send", auditory=auditory).pack()
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text=_("📅 Запланировать рассылку"),
            callback_data=BroadcastCallback(action="schedule", auditory=auditory).pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("↩️ Назад"),
            callback_data=back_callback.pack(),
        )
    )

    return builder.as_markup()

def confirm_broadcast_keyboard(auditory: str, back_callback: CallbackData) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=_("✅ Отправить"),
            callback_data=BroadcastCallback(action="confirm", auditory=auditory).pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=_("❌ Отменить"),
            callback_data=BroadcastCallback(action="reject", auditory=auditory).pack(),
        )
    )

    return builder.as_markup()