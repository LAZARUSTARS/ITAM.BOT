import typing as tp
from aiogram import types

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from bot.keyboards.menu import MainMenuCallback, CoworkingMenuCallback
from .broadcast import BroadcastCallback
from repositories.coworking.models import CoworkingStatus, COWORKING_ACTIONS


class CoworkingStatusCallback(CallbackData, prefix="coworking_status"):
    action: tp.Optional[COWORKING_ACTIONS] = None
    gain_control: bool = False
    duration: tp.Optional[int] = None
    input_duration: bool = False

def coworking_admin_input_duration_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=_("↩️ Назад"),
        callback_data=CoworkingMenuCallback(action="admin_menu"),
    )
    builder.adjust(1)
    return builder.as_markup()


def coworking_admin_keyboard(
    coworking_data: CoworkingStatusCallback,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
            types.InlineKeyboardButton(
                text=_("Рассылка для подписчиков 📢"),
                callback_data=BroadcastCallback(action="menu", auditory="coworking").pack(),
            ),
        )
    match coworking_data.action:
        case None:
            builder.button(
                text=_("Открыть коворкинг"),
                callback_data=CoworkingStatusCallback(action=CoworkingStatus.OPEN),
            )
            builder.button(
                text=_("Coworking admin status change to close inline keyboard button"),
                callback_data=CoworkingStatusCallback(action=CoworkingStatus.CLOSE),
            )
            builder.adjust(1)
        case CoworkingStatus.OPEN:
            builder.button(
                text=_("Открыть коворкинг"),
                callback_data=CoworkingStatusCallback(action=CoworkingStatus.OPEN),
            )
            # builder.button(
            #     text=_("Coworking admin status change to close inline keyboard button"),
            #     callback_data=CoworkingStatusCallback(action=CoworkingStatus.CLOSE),
            # )
            builder.adjust(1)
        case CoworkingStatus.CLOSE:
            if coworking_data.duration is None:
                if coworking_data.gain_control:
                    builder.button(
                        text=_("Взять ответственность на себя"),
                        callback_data=CoworkingStatusCallback(
                            action=CoworkingStatus.GAIN_CONTROL,
                        ),
                    )
                    builder.adjust(1)
                builder.button(
                    text=_("Закрыть до завтра"),
                    callback_data=CoworkingStatusCallback(
                        action=CoworkingStatus.CLOSE, duration=-1
                    ),
                )

                builder.button(
                    text=_("🚧 на 30 минут"),
                    callback_data=CoworkingStatusCallback(
                        action=CoworkingStatus.CLOSE, duration=30
                    ),
                )
                builder.button(
                    text=_("🚧 на 60 минут"),
                    callback_data=CoworkingStatusCallback(
                        action=CoworkingStatus.CLOSE, duration=60
                    ),
                )
                builder.button(
                    text=_("Ввести время"),
                    callback_data=CoworkingStatusCallback(
                        action=CoworkingStatus.CLOSE, input_duration=True
                    ),
                )
                builder.adjust(1)

            else:
                builder.button(
                    text=_("Открыть коворкинг"),
                    callback_data=CoworkingStatusCallback(action=CoworkingStatus.OPEN),
                )
                builder.button(
                    text=_("Закрыть коворкинг"),
                    callback_data=CoworkingStatusCallback(action=CoworkingStatus.CLOSE),
                )
                builder.adjust(1)

    builder.button(
        text=_("↩️ Назад"),
        callback_data=MainMenuCallback(next_menu_prefix="coworking"),
    )
    builder.adjust(1)
    return builder.as_markup()
