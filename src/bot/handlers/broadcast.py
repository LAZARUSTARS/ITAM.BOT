import typing as tp
import datetime as dt

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, types, Router, F
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from ..settings import Settings


from repositories.users.base import UserRepositoryBase
from repositories.users.models import TelegramUser
from utils import schedule_custom_broadcast, send_broadcast, get_all_jobs

from ..keyboards.menu import MainMenuCallback, CoworkingMenuCallback, ClubsMenuCallback
from ..keyboards.broadcast import BroadcastCallback, broadcast_keyboard, confirm_broadcast_keyboard

router: tp.Final[Router] = Router(name="broadcast")

class BroadcastStates(StatesGroup):
    get_text = State()
    get_date = State()
    confirm = State()

def get_correct_back_callback(auditory: str) -> BroadcastCallback:
    if "club" in auditory:
        return ClubsMenuCallback(club=auditory)
    else:
        return MainMenuCallback(next_menu_prefix="ITAM")

@router.callback_query(BroadcastCallback.filter(F.action == "menu"))
async def broadcast_menu(
    callback: types.CallbackQuery,
    callback_data: BroadcastCallback,
    scheduler: AsyncIOScheduler,
    ) -> None:
    msg_text = _("broadcast menu text")
    auditory = callback_data.auditory
    print("------")
    print(auditory)
    print("------")
    back_callback = get_correct_back_callback(auditory)
    if callback.message:
        scheduled_messages = get_all_jobs(scheduler, auditory)
        await callback.message.edit_text(
            msg_text,
            reply_markup=broadcast_keyboard(auditory, back_callback, scheduled_messages),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=broadcast_keyboard(auditory, back_callback, scheduled_messages),
        )

@router.callback_query(BroadcastCallback.filter((F.action == "send") | (F.action == "schedule")))
async def broadcast_send_input_text(
    callback: types.CallbackQuery,
    callback_data: BroadcastCallback,
    state: FSMContext,
    ) -> None:
    msg_text = _("Введите текст для рассылки")
    auditory = callback_data.auditory
    action = callback_data.action
    print("------")
    print(auditory)
    print("------")
    if callback.message:
        await callback.message.edit_text(
            msg_text,
        )
    else:
        await callback.answer(
            msg_text,
        )
    await state.set_state(BroadcastStates.get_text)
    # put data to state
    await state.update_data(auditory=auditory)
    await state.update_data(action=action)

@router.message(BroadcastStates.get_text)
async def broadcast_send_input_date(
    message: types.Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    tg_user: TelegramUser,
    ) -> None:
    data = await state.get_data()
    action = data.get("action")
    await state.update_data(text=message.text)

    if action == "send":
        auditory=data.get("auditory")
        print("------")
        print(action)
        print(auditory)
        print("------")
        msg_text = _("Подтвердите отправку текста:\n {text}\n Получатели: {auditory}").format(
            text=message.text,
            auditory=auditory,
        )
        back_callback = get_correct_back_callback(auditory)
        await state.set_state(BroadcastStates.confirm)
        await message.answer(
            msg_text,
            reply_markup=confirm_broadcast_keyboard(auditory, back_callback),
        )

    elif action == "schedule":
        msg_text = _("Введите дату и время в формате YYYY-MM-DD HH:MM")
        await state.set_state(BroadcastStates.get_date)
        await message.answer(msg_text)

@router.message(BroadcastStates.get_date)
async def broadcast_send_confirm(
    message: types.Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    tg_user: TelegramUser,
    ) -> None:
    auditory=(await state.get_data()).get("auditory")
    text=(await state.get_data()).get("text")
    try:
        date = dt.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(_("Неверный формат даты"))
        return

    msg_text = _("Подтвердите отправку текста:\n {text}\n Получатели: {auditory}\n Дата и время: {date}").format(
        text=text,
        auditory=auditory,
        date=date.strftime("%Y-%m-%d %H:%M"),
    )
    back_callback = get_correct_back_callback(auditory)
    await state.set_state(BroadcastStates.confirm)
    await state.update_data(date=date)
    await message.answer(
        msg_text,
        reply_markup=confirm_broadcast_keyboard(auditory, back_callback),
    )


@router.callback_query(BroadcastCallback.filter(F.action == "confirm"))
async def broadcast_send(
    callback: types.CallbackQuery,
    callback_data: BroadcastCallback,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    user_repo: UserRepositoryBase,
    bot: Bot,
    ) -> None:
    """Send broadcast message or schedule it"""
    data = await state.get_data()
    auditory = data.get("auditory")
    text = data.get("text")
    action = data.get("action")
    await state.clear()
    # get users from auditory
    userlist = user_repo.get_broadcast_users(auditory)
    if action == "send":
        await callback.message.edit_text(_("Рассылка начата"), reply_markup=None)
        await send_broadcast(bot=bot, message=text, users=userlist)
        await callback.answer()
    elif action == "schedule":
        date: dt.datetime = data.get("date")
        await schedule_custom_broadcast(
            bot=bot,
            scheduler=scheduler,
            date_time_exec=date,
            message=text,
            users=userlist,
            schedule_id=f'{auditory}_{date.strftime("%Y-%m-%d %H-%M")}',
        )
        await callback.message.edit_text(_("Рассылка запланирована"))
        await callback.answer(_("Рассылка запланирована"))

@router.callback_query(BroadcastCallback.filter(F.action == "reject"))
async def broadcast_send_reject(
    callback: types.CallbackQuery,
    callback_data: BroadcastCallback,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
    ) -> None:
    await state.clear()
    auditory = callback_data.auditory
    back_callback = get_correct_back_callback(auditory)
    scheduled_messages = get_all_jobs(scheduler, auditory)
    await callback.message.edit_text(
        _("broadcast menu text"),
        reply_markup=broadcast_keyboard(auditory, back_callback, scheduled_messages),
    )

@router.callback_query(BroadcastCallback.filter(F.action.startswith("cancel_")))
async def broadcast_cancel(
    callback: types.CallbackQuery,
    callback_data: BroadcastCallback,
    scheduler: AsyncIOScheduler,
    ) -> None:
    job_id = callback_data.action.split("cancel_")[-1]
    scheduler.remove_job(job_id)
    auditory = callback_data.auditory
    back_callback = get_correct_back_callback(auditory)
    scheduled_messages = get_all_jobs(scheduler, auditory)
    await callback.message.edit_text(
        _("удалена рассылка {job_id}").format(job_id=job_id),
        reply_markup=broadcast_keyboard(auditory, back_callback, scheduled_messages),
    )
