import asyncio
import typing as tp
from aiogram import Bot, types, Router, F

from aiogram.filters import and_f
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from repositories.users.base import UserRepositoryBase

from controllers.coworking import CoworkingController
from repositories.coworking.models import CoworkingStatus, COWORKING_ACTIONS

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from repositories.users.models import TelegramUser

import datetime as dt


from ..keyboards.menu import (
    coworking_menu_keyboard,
    MainMenuCallback,
    CoworkingMenuCallback,
    SubscriptionCallback,
)
# from ..keyboards.coworking import coworking_subscription,
from ..keyboards.coworking_admin import (
    CoworkingStatusCallback,
    coworking_admin_keyboard,
    coworking_admin_input_duration_keyboard,
)
from utils import (
    get_user_mention,
    send_broadcast,
    schedule_coworking_status,
    cancel_schedule_job,
    schedule_coworking_status_broadcast,
    schedule_autoclose_coworking,
    cancel_autoclose_coworking
    )

router: tp.Final[Router] = Router(name="coworking")

class CoworkingStatusState(StatesGroup):
    duration = State()

class OverTimeDuration(Exception):
    pass

def has_admin_rights(tg_user: TelegramUser) -> bool:
    return "coworking" in tg_user.admin_rights.right_model.values()

@router.callback_query(MainMenuCallback.filter(F.next_menu_prefix == "coworking"))
async def coworking_menu(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
    ) -> None:
    msg_text = _("coworking menu text")
    subscribed = coworking_controller.is_subscribed(tg_user.tg_id)
    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), subscribed),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), subscribed),
        )


# @router.callback_query(CoworkingMenuCallback.filter(F.action == "info"))
# async def coworking_info(callback: types.CallbackQuery, tg_user: TelegramUser) -> None:
#     msg_text = _("coworking info text")

#     if callback.message:
#         await callback.message.edit_text(
#             msg_text,
#             reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user)),
#         )
#     else:
#         await callback.answer(
#             msg_text,
#             reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user)),
#         )


@router.callback_query(CoworkingMenuCallback.filter(F.action == "status"))
async def coworking_status(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
) -> None:
    status: CoworkingStatus | None = coworking_controller.get_status()
    subscribed = coworking_controller.is_subscribed(tg_user.tg_id)

    if status is None:
        msg_text = _("coworking status text if status is None")
    else:
        if status.duration:
            msg_text = _("coworking closed until {due} {mention}").format(
                due=dt.datetime.strftime(status.time+dt.timedelta(minutes=status.duration), "%H:%M"),
                mention=status.responsible_mention
            )
        else:
            if status.status == 'open':
                msg_text = _("coworking open {mention}").format(mention=status.responsible_mention)
            else: msg_text = _("coworking closed {mention}").format(mention=status.responsible_mention)

    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), subscribed, in_status=True),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), subscribed, in_status=True),
        )

@router.callback_query(SubscriptionCallback.filter(F.subscribed == True))
async def coworking_unsubscribe(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
) -> None:
    msg_text = _("Ты отписался от уведомлений о статусе коворкинга")
    coworking_controller.subscribe_user(tg_user.tg_id, False)

    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), False),
        )
        await callback.answer()
    else:
        await callback.answer(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), False),
        )


@router.callback_query(SubscriptionCallback.filter(F.subscribed == False))
async def coworking_subscribe(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
) -> None:

    msg_text = _("Ты подписался на уведомления о статусе коворкинга")

    coworking_controller.subscribe_user(tg_user.tg_id, True)

    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), True),
        )
        await callback.answer()
    else:
        await callback.answer(
            msg_text,
            reply_markup=coworking_menu_keyboard(has_admin_rights(tg_user), True),
        )


@router.callback_query(CoworkingMenuCallback.filter(F.action == "admin_menu"))
async def coworking_admin_menu(
    callback: types.CallbackQuery,
    coworking_controller: CoworkingController,
    tg_user: TelegramUser,
    state: FSMContext,
    ) -> None:
    # finish if state is not finished
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    msg_text = _("coworking admin menu text")
    status = coworking_controller.get_status()
    gain_control = status.responsible_mention != get_user_mention(tg_user)
    # revert status for keyboard
    if status:
        if status.status == CoworkingStatus.OPEN:
            status = CoworkingStatus.CLOSE
        else:
            status = CoworkingStatus.OPEN
    else:
        status = CoworkingStatus.OPEN
    if callback.message:
        await callback.message.edit_text(
            msg_text,
            reply_markup=coworking_admin_keyboard(CoworkingStatusCallback(action=status, gain_control=gain_control)),
        )
    else:
        await callback.answer(
            msg_text,
            reply_markup=coworking_admin_keyboard(CoworkingStatusCallback(action=status, gain_control=gain_control)),
        )


@router.callback_query(CoworkingStatusCallback.filter(F.action == None))
async def coworking_status_menu(
    callback: types.CallbackQuery,
    callback_data: CoworkingStatusCallback,
) -> None:
    msg_text = _("Меню администратора для управления статусом ковркинга")
    markup = coworking_admin_keyboard(callback_data)
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(
            msg_text,
            reply_markup=markup,
        )

@router.callback_query(
    CoworkingStatusCallback.filter(F.action == CoworkingStatus.GAIN_CONTROL)
)
async def coworking_status_gain_control(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
    scheduler: AsyncIOScheduler,
    bot: Bot,
) -> None:
    coworking_controller.set_status(tg_user.tg_id, CoworkingStatus.OPEN)  # type: ignore проверено в фильтре
    mention = get_user_mention(tg_user)
    # reasssign autoclose
    await schedule_autoclose_coworking(bot, scheduler, coworking_controller, tg_user)

    msg_text = _("<b>Теперь вы отвественный за коворкинг</b>\n🟢 Коворкинг ITAM открыт \n\nОтветственный: {mention}").format(
        mention=mention
    )
    markup = coworking_admin_keyboard(CoworkingStatusCallback(action=CoworkingStatus.CLOSE))
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(
            msg_text,
            reply_markup=markup,
        )


# @router.callback_query(
#     and_f(
#         CoworkingStatusCallback.filter(F.action == CoworkingStatus.CLOSE),
#         CoworkingStatusCallback.filter(F.duration == None),
#     )
# )
# async def coworking_status_duration_selector(
#     callback: types.CallbackQuery,
#     callback_data: CoworkingStatusCallback,
# ) -> None:
#     msg_text = _("Coworking admin status close durations selection")
#     markup = coworking_admin_keyboard(callback_data)
#     if callback.message:
#         await callback.message.edit_text(msg_text, reply_markup=markup)
#         await callback.answer()
#     else:
#         await callback.answer(
#             msg_text,
#             reply_markup=markup,
#         )

@router.callback_query(
    CoworkingStatusCallback.filter(
        F.action == CoworkingStatus.CLOSE and F.input_duration == True
    )
)
async def coworking_status_duration_input(
    callback: types.CallbackQuery,
    callback_data: CoworkingStatusCallback,
    state: FSMContext,
) -> None:
    msg_text = _("Введите время в минутах")
    await state.set_state(CoworkingStatusState.duration)
    markup = coworking_admin_input_duration_keyboard()
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(msg_text, reply_markup=markup)

@router.message(CoworkingStatusState.duration)
async def coworking_status_duration_input_handler(
    message: types.Message,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
    scheduler: AsyncIOScheduler,
    bot: Bot,
    state: FSMContext,
) -> None:
    try:
        duration = int(message.text)
        if dt.datetime.now() + dt.timedelta(minutes=duration) > dt.datetime.now().replace(hour=20, minute=0):
            raise OverTimeDuration("closed_over_8PM")
    except ValueError:
        await message.answer(_("Введите валидное число"), reply_markup=coworking_admin_input_duration_keyboard())
        return
    except OverTimeDuration:
        await message.answer(_("Открытие коворкинга должно произойти до 20:00"), reply_markup=coworking_admin_input_duration_keyboard())
        return
    await state.clear()
    # call existing handler with duration
    await coworking_status_close(
        message,
        tg_user,
        coworking_controller,
        CoworkingStatusCallback(action=CoworkingStatus.CLOSE, duration=duration),
        scheduler,
        bot,
    )


@router.callback_query(
    CoworkingStatusCallback.filter(
        F.action == CoworkingStatus.CLOSE and F.duration != None
    )
)
async def coworking_status_close(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
    callback_data: CoworkingStatusCallback,
    scheduler: AsyncIOScheduler,
    bot: Bot,
) -> None:

    coworking_controller.set_status(
        tg_user.tg_id,
        callback_data.action,  # type: ignore ( т.к. проверяем в фильтре)
        callback_data.duration if callback_data.duration > 0 else None,  # type: ignore ( т.к. проверяем в фильтре)
    )
    mention = get_user_mention(tg_user)
    if callback_data.duration == -1:
        # cancel all scheduled jobs
        await cancel_schedule_job(scheduler, "coworking_status")
        await cancel_schedule_job(scheduler, "coworking_status_broadcast")
        await cancel_autoclose_coworking(scheduler)

        msg_text = _("🔑🔴 Коворкинг ITAM закрыт \n\nОтветственный: {mention}").format(
            mention=mention
        )
    else:
        await schedule_coworking_status(
            scheduler,
            coworking_controller,
            tg_user.tg_id,
            CoworkingStatus(
                status=CoworkingStatus.OPEN,
                duration=callback_data.duration,
                responsible_mention=mention,
                time=dt.datetime.now(),
            )
        )
        msg_text_broadcast = _("🟢 Коворкинг ITAM открыт \n\nОтветственный: {mention}").format(
            mention=mention
        )
        await schedule_coworking_status_broadcast(
            bot,
            scheduler,
            dt.datetime.now() + dt.timedelta(minutes=callback_data.duration),
            msg_text_broadcast,
            coworking_controller.get_subscribed_ids(),
        )
        msg_text = _(
            "🔑🔴 Коворкинг ITAM закрыт на {duration} минут \n\nОтветственный: {mention}"
        ).format(duration=callback_data.duration, mention=mention)

    markup = coworking_admin_keyboard(CoworkingStatusCallback(action=CoworkingStatus.OPEN))
    if isinstance(callback, types.CallbackQuery) and callback.message:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(
            msg_text,
            reply_markup=markup,
        )

    # уведомление пользователей об изменении статуса коворкинга
    await send_broadcast(bot, msg_text, coworking_controller.get_subscribed_ids())
    # subscribed = coworking_controller.get_subscribed_ids()
    # print(subscribed)
    # for i in subscribed:
    #     await asyncio.sleep(0.2)
    #     await bot.send_message(i, msg_text)
    # await asyncio.gather(*[bot.send_message(u_id, msg_text) for u_id in subscribed])


@router.callback_query(CoworkingStatusCallback.filter(F.action == CoworkingStatus.OPEN))
async def coworking_status_open(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
    coworking_controller: CoworkingController,
    callback_data: CoworkingStatusCallback,
    scheduler: AsyncIOScheduler,
    bot: Bot,
) -> None:

    coworking_controller.set_status(tg_user.tg_id, callback_data.action)  # type: ignore проверено в фильтре
    mention = get_user_mention(tg_user)

    msg_text = _("🟢 Коворкинг ITAM открыт \n\nОтветственный: {mention}").format(
        mention=mention
    )
    await cancel_schedule_job(scheduler, "coworking_status")
    await cancel_schedule_job(scheduler, "coworking_status_broadcast")
    # schedule autoclose
    await schedule_autoclose_coworking(bot, scheduler, coworking_controller, tg_user)
    markup = coworking_admin_keyboard(CoworkingStatusCallback(action=CoworkingStatus.CLOSE))
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(
            msg_text,
            reply_markup=markup,
        )

    # уведомление пользователей об изменении статуса коворкинга
    await send_broadcast(bot, msg_text, coworking_controller.get_subscribed_ids())
    # subscribed = coworking_controller.get_subscribed_ids()
    # for i in subscribed:
    #     await asyncio.sleep(0.2)
    #     await bot.send_message(i, msg_text)
    # await asyncio.gather(*[bot.send_message(u_id, msg_text) for u_id in subscribed])
