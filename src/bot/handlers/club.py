import asyncio
import typing as tp
from aiogram import Bot, types, Router, F

from aiogram.filters import and_f
from aiogram.utils.i18n import gettext as _

from controllers.club import ClubController
from repositories.users.models import TelegramUser
from repositories.club.models import ClubInfo

from aiogram.utils.markdown import hide_link

from ..keyboards.menu import (
    clubs_menu_keyboard,
    MainMenuCallback,
    ClubsMenuCallback,
)

from ..keyboards.clubs import club_subscription_and_info, SubscriptionCallback

router: tp.Final[Router] = Router(name="clubs")

def has_admin_rights(tg_user: TelegramUser, club: str) -> bool:
    return club in tg_user.admin_rights.right_model.values()

@router.callback_query(MainMenuCallback.filter(F.next_menu_prefix == "clubs"))
async def clubs_menu(callback: types.CallbackQuery) -> None:
    msg_text = _("clubs menu text")
    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=clubs_menu_keyboard(),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=clubs_menu_keyboard(),
        )

# get all clubcalbacks witthout a filter and parse text in 'next_menu_prefix' to get the name of the club
@router.callback_query(ClubsMenuCallback.filter())
async def clubs_info(
    callback: types.CallbackQuery,
    callback_data: ClubsMenuCallback,
    club_controller: ClubController,
    tg_user: TelegramUser,
    ) -> None:
    club = str(callback_data.club)
    club_info = club_controller.get_club_info(club)
    subscribed = club_controller.is_subscribed(tg_user.tg_id, club)
    msg_text = _("club info {description} {link}").format(
        description=club_info.description,
        link=hide_link(club_info.link),
    )
    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=club_subscription_and_info(
                 subscribed, club, club_info.link, club_info.additional_links,
                 has_admin_rights(tg_user, club)
            ),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=club_subscription_and_info(
                 subscribed, club, club_info.link, club_info.additional_links,
                 has_admin_rights(tg_user, club)
            ),
        )

@router.callback_query(SubscriptionCallback.filter())
async def club_subscription(
    callback: types.CallbackQuery,
    callback_data: SubscriptionCallback,
    club_controller: ClubController,
    tg_user: TelegramUser,
    ) -> None:
    club = str(callback_data.club)
    club_controller.set_club_notifications(tg_user.tg_id, callback_data.subscribed, club)
    subscribed = club_controller.is_subscribed(tg_user.tg_id, club)
    club_info = club_controller.get_club_info(club)
    msg_text = _("club info\n{description}\n{link}").format(
        description=club_info.description,
        link=hide_link(club_info.link),
    )
    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=club_subscription_and_info(
                 subscribed, club, club_info.link, club_info.additional_links,
                 has_admin_rights(tg_user, club)
            ),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=club_subscription_and_info(
                 subscribed, club, club_info.link, club_info.additional_links,
                 has_admin_rights(tg_user, club)
            ),
        )