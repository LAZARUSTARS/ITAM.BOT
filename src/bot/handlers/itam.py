import asyncio
import typing as tp
from aiogram import Bot, types, Router, F

from aiogram.filters import and_f
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from repositories.users.models import TelegramUser

import datetime as dt

from ..keyboards.menu import (
    MainMenuCallback
)
from ..keyboards.itam import (
    itam_menu,
    digest_keyborad,
    ITAMMenuCallback,
    DigestMenuCallback
)

router: tp.Final[Router] = Router(name="itam")

def has_admin_rights_itam(tg_user: TelegramUser) -> bool:
    return "itam_broadcast" in tg_user.admin_rights.right_model.values()

def has_admin_rights_digest(tg_user: TelegramUser) -> bool:
    return "digest" in tg_user.admin_rights.right_model.values()

@router.callback_query(MainMenuCallback.filter(F.next_menu_prefix == "ITAM"))
async def itam_menu_callback(callback: types.CallbackQuery, tg_user: TelegramUser):
    msg_text = _("ITAM menu")
    await callback.message.edit_text(
        text=msg_text,
        reply_markup=itam_menu(is_admin=has_admin_rights_itam(tg_user))
    )

@router.callback_query(ITAMMenuCallback.filter(F.action == "contacts"))
async def itam_contacts_callback(callback: types.CallbackQuery, tg_user: TelegramUser):
    msg_text = _("ITAM contacts")
    await callback.message.edit_text(
        text=msg_text,
        reply_markup=itam_menu(in_contacts=True, is_admin=has_admin_rights_itam(tg_user)),
        disable_web_page_preview=True
    )

@router.callback_query(ITAMMenuCallback.filter(F.action == "about"))
async def itam_about_callback(callback: types.CallbackQuery, tg_user: TelegramUser):
    msg_text = _("ITAM menu")
    await callback.message.edit_text(
        text=msg_text,
        reply_markup=itam_menu(is_admin=has_admin_rights_itam(tg_user))
    )

