from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from controllers.coworking import CoworkingController
from repositories.coworking.models import CoworkingStatus, COWORKING_ACTIONS
from repositories.users.models import TelegramUser
from aiogram import Bot
from utils.broadcast import schedule_custom_broadcast, schedule_coworking_status_broadcast
from utils import get_user_mention
import logging
from datetime import datetime as dt
from datetime import timedelta
import typing as tp

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

async def schedule_autoclose_coworking(
        bot: Bot,
        scheduler: AsyncIOScheduler,
        coworking_controller: CoworkingController,
        tg_user: TelegramUser) -> None:
    """
    Schedule autoclose coworking at 10:00 PM"""
    execute_time = dt.now().replace(hour=22, minute=0, second=0, microsecond=0)
    try:
        scheduler.add_job(
            coworking_controller.set_status,
            "date",
            run_date=execute_time,
            args=[tg_user.tg_id , CoworkingStatus.CLOSE, None],
            id="coworking_autoclose",
            replace_existing=True,
        )
        mention = get_user_mention(tg_user)
        log.info("Coworking autoclose status scheduled")
        msg_text = "🔑🔴 Коворкинг ITAM закрыт \n\nОтветственный: {mention}".format(
            mention=mention
        )

        # schedule broadcast about autoclose
        await schedule_custom_broadcast(
            bot=bot,
            scheduler=scheduler,
            date_time_exec=execute_time,
            message=msg_text,
            users=coworking_controller.get_subscribed_ids(),
            schedule_id="coworking_autoclose_broadcast"
        )

        # schdule broadcast to specific admins about autoclose
        # TODO: get this admins from settings or db
        await schedule_custom_broadcast(
            bot=bot,
            scheduler=scheduler,
            date_time_exec=execute_time,
            message=f"<b>Наршуение правил закрытия коворка!</b>\n Проебался {mention}",
            users=[257836233, 141576047],
            schedule_id="coworking_autoclose_broadcast_admins"
        )
    except JobLookupError:
        log.exception("Coworking autoclose scheduling failed")

async def cancel_autoclose_coworking(scheduler: AsyncIOScheduler) -> None:
    """
    Cancel scheduled autoclose coworking"""
    await cancel_schedule_job(scheduler, "coworking_autoclose")
    await cancel_schedule_job(scheduler, "coworking_autoclose_broadcast")
    await cancel_schedule_job(scheduler, "coworking_autoclose_broadcast_admins")

async def schedule_coworking_status(
        scheduler: AsyncIOScheduler,
        coworking_controller: CoworkingController,
        tg_id: int,
        status: CoworkingStatus) -> None:
    try:
        scheduler.add_job(
            coworking_controller.set_status,
            "date",
            run_date=dt.now() + timedelta(minutes=status.duration),
            args=[tg_id, status.status, None],
            id="coworking_status",
            replace_existing=True,
        )
        log.info("Coworking status scheduled")
    except JobLookupError:
        log.exception("Coworking status scheduling failed")

async def cancel_schedule_job(scheduler: AsyncIOScheduler, job_id: str) -> None:
    """
    Cancel scheduled broadcast

    :param scheduler:
    :param job_id:
    :return:
    """
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        log.error(f"Job {job_id} not found")
    else:
        log.info(f"Job {job_id} canceled")
