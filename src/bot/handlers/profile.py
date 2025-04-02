"""
1. Возможность редактировать следующие параметры:
    1. ФИО
    2. Ник в telegram
    3. Корпоративная почта МИСИС (в домене @edu.misis.ru)
    4. Учебная группа
    5. Ссылка на GitHub репозиторий
    6. Направление — frontend, backend и т д
    7. Навыки — стек технологий в рамках направления
    8. Ссылки — гит, резюме и прочие
    9. Готовность помогать новичкам — готов/не готов
    10. в какой компании работает
Подумать насчет экспортом в гугл докс
И как это хранить в бд?)
"""

import typing as tp
import datetime as dt

from aiogram import Bot, types, Router, F
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from ..settings import Settings


from repositories.users.base import UserRepositoryBase
from utils import users_table, get_admin_invite_link, create_invite_code

from ..keyboards.menu import MainMenuCallback, base_menu_reply_key
from ..keyboards.profile import (
    ProfileMenuCallback,
    ProfileAdminMenuCallback,
    MajorCallback,
    MentorStatusCallback,
    AddAdminCallback,
    profile_menu_keyboard,
    mentor_status_keyboard,
    field_selector_menu,
    editing_keyboard,
    admin_menu_keyboard,
    PROFILE_EDITABLE_FIELD,
    AVALIABLE_PROFESSIONS,
    majors_keyboard,
    select_admin_rights_keyboard,
)
from repositories.users.models import TelegramUser

router: tp.Final[Router] = Router(name="profile")


class ProfileForm(StatesGroup):
    field_name = State()  # to track current editing field

    editing = State()
    fio = State()
    email = State()
    educational_group = State()
    portfolio_link = State()
    majors = State()
    skills = State()
    external_links = State()
    mentor_status = State()
    company = State()

class ProfileAdminForm(StatesGroup):
    timestamp = State()


def has_admin_rights(tg_user: TelegramUser) -> bool:
    return "profiles" in tg_user.admin_rights.right_model.values()

# TODO: move to messages block
def get_editing_text(tg_user: TelegramUser) -> str:
    if tg_user.profile:
        return _(
            "Что ты хочешь отредактировать?\n\n<b>ФИО:</b>\n{fio}\n<b>Почта:</b>\n{email}\n<b>Учебная группа:</b>\n{group}\n<b>Ссылка на портфолио:</b>\n{portfolio}\n<b>Направления разработки:</b>\n{majors}\n<b>Навыки/Стэк технолгий:</b>\n{skills}\n<b>Ссылки на соц. сети:</b>\n{links}\n<b>Готовность стать ментором:</b>\n{mentor}\n<b>Компания:</b>\n{company}"
        ).format(
            fio=tg_user.profile.fio if tg_user.profile.fio else _("Не указано"),
            email=tg_user.profile.email if tg_user.profile.email else _("Не указано"),
            group=tg_user.profile.educational_group
            if tg_user.profile.educational_group
            else _("Не указано"),
            portfolio=tg_user.profile.portfolio_link
            if tg_user.profile.portfolio_link
            else _("Не указано"),
            majors=", ".join(tg_user.profile.majors)
            if tg_user.profile.majors
            else _("Не указано"),
            skills=", ".join(tg_user.profile.skills)
            if tg_user.profile.skills
            else _("Не указано"),
            links=", ".join(tg_user.profile.external_links)
            if tg_user.profile.external_links
            else _("Не указано"),
            mentor=_("Yes") if tg_user.profile.mentor_status else _("No"),
            company=tg_user.profile.company if tg_user.profile.company else _("Не указано"),
        )
    else:
        return _("Профиль не заполнен(\nЧто ты хочешь отредактировать?")

def get_profifle_text(tg_user: TelegramUser) -> str:
    if tg_user.profile:
        return _(
            "<b>⚙️ Профиль</b>\n\n<b>ФИО:</b>\n{fio}\n<b>Почта:</b>\n{email}\n<b>Учебная группа:</b>\n{group}\n<b>Ссылка на портфолио:</b>\n{portfolio}\n<b>Направления разработки:</b>\n{majors}\n<b>Навыки/Стэк технолгий:</b>\n{skills}\n<b>Ссылки на соц. сети:</b>\n{links}\n<b>Готовность стать ментором:</b>\n{mentor}\n<b>Компания:</b>\n{company}\n\n"
        ).format(
            fio=tg_user.profile.fio if tg_user.profile.fio else _("Не указано"),
            email=tg_user.profile.email if tg_user.profile.email else _("Не указано"),
            group=tg_user.profile.educational_group
            if tg_user.profile.educational_group
            else _("Не указано"),
            portfolio=tg_user.profile.portfolio_link
            if tg_user.profile.portfolio_link
            else _("Не указано"),
            majors=", ".join(tg_user.profile.majors)
            if tg_user.profile.majors
            else _("Не указано"),
            skills=", ".join(tg_user.profile.skills)
            if tg_user.profile.skills
            else _("Не указано"),
            links=", ".join(tg_user.profile.external_links)
            if tg_user.profile.external_links
            else _("Не указано"),
            mentor=_("Yes") if tg_user.profile.mentor_status else _("No"),
            company=tg_user.profile.company if tg_user.profile.company else _("Не указано"),
        )
    else:
        return _("Профиль не заполнен(\nЧто ты хочешь отредактировать?")

@router.callback_query(MainMenuCallback.filter(F.next_menu_prefix == "profile"))
async def profile_menu_callbacks(
    callback: types.CallbackQuery, tg_user: TelegramUser
) -> None:
    msg_text = get_profifle_text(tg_user)+_("ProfileMenu text")

    markup = profile_menu_keyboard(tg_user.is_admin)
    if not callback.message:
        await callback.answer(
            text=msg_text,
            reply_markup=markup,
        )
    else:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()


async def process_editing(
    state: FSMContext,
    callback: types.CallbackQuery,
    callback_data: ProfileMenuCallback,
    tg_user: TelegramUser,
) -> None:
    # FIXME: split into different handlers
    msg_text: str = _("Error")
    markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | types.ReplyKeyboardRemove | types.ForceReply | None = (
        base_menu_reply_key()
    )
    if len((await state.get_data()).keys()) == 0:
        await state.update_data(tg_user=tg_user)
    match callback_data.field:
        case "fio":
            msg_text = _("Введи свое ФИО через пробел")
            markup = editing_keyboard(next_input=True)
            await state.set_state(ProfileForm.fio)
        case "email":
            msg_text = _("Введи свой email в домене edu.misis.ru")
            markup = editing_keyboard()
            await state.set_state(ProfileForm.email)
        case "educational_group":
            msg_text = _("Введи свою учебную группу (пример: БИВТ)")
            markup = editing_keyboard()
            await state.set_state(ProfileForm.educational_group)
        case "portfolio_link":
            msg_text = _(
                "Ссылка на портфолио с проектами (github/gitlab/notion/etc...)"
            )
            markup = editing_keyboard(next_input=True)
            await state.set_state(ProfileForm.portfolio_link)
        case "majors":
            msg_text = _("Выбери направления разработки, в которых ты специализируешься")
            markup = majors_keyboard(','.join([key for key, value in AVALIABLE_PROFESSIONS.items() if value in tg_user.profile.majors]) if tg_user.profile.majors else '')
            await state.set_state(ProfileForm.majors)
        case "skills":
            msg_text = _("Выбери стек технологий с которымы ты хорошо знаком")
            markup = editing_keyboard(next_input=True)
            await state.set_state(ProfileForm.skills)
        case "external_links":
            msg_text = _(
                "Тут ты можешь оставить дополнительные ссылки на соцсети / резюме"
            )
            markup = editing_keyboard(next_input=True)
            await state.set_state(ProfileForm.external_links)
        case "mentor_status":
            msg_text = _("Готов ли ты стать ментором")
            markup = mentor_status_keyboard()
            await state.set_state(ProfileForm.mentor_status)
        case "company":
            msg_text = _("Введи название компании, в которой ты работаешь, и должность (если есть)")
            markup = editing_keyboard(next_input=True)
            await state.set_state(ProfileForm.company)

    if callback.message:
        if isinstance(markup, types.ReplyKeyboardRemove):
            markup = None
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(
            text=msg_text,
            reply_markup=markup,
        )


async def sync_profile_data(
    user_repo: UserRepositoryBase, tg_user: TelegramUser, user_data: dict | None
) -> TelegramUser:
    if user_data and "tg_user" in user_data.keys():
        tg_user = user_data["tg_user"]
        user_repo.save_profile_data(tg_user.tg_id, **tg_user.profile.model_dump())
        return tg_user
    else:
        return tg_user


@router.callback_query(ProfileMenuCallback.filter(F.action == None))
async def profile_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user: TelegramUser,
    user_repo: UserRepositoryBase,
) -> None:

    markup = profile_menu_keyboard(tg_user.is_admin)
    tg_user = await sync_profile_data(user_repo, tg_user, await state.get_data())
    msg_text = get_profifle_text(tg_user)+_("ProfileMenu text")

    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer(
            text=msg_text,
            reply_markup=markup,
        )


@router.callback_query(ProfileMenuCallback.filter(F.action == "user_form"))
async def profile_data(
    callback: types.CallbackQuery,
    callback_data: ProfileMenuCallback,
    state: FSMContext,
    tg_user: TelegramUser,
    user_repo: UserRepositoryBase,
) -> None:

    tg_user = await sync_profile_data(user_repo, tg_user, await state.get_data())
    msg_text = get_editing_text(tg_user=tg_user)
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=field_selector_menu())
        await callback.answer(text=_("Данные сохранены"))
    else:
        await callback.answer(msg_text, reply_markup=field_selector_menu())


@router.callback_query(ProfileMenuCallback.filter(F.action == "editing"))
async def profile_editing(
    callback: types.CallbackQuery,
    callback_data: ProfileMenuCallback,
    state: FSMContext,
    tg_user: TelegramUser,
    user_repo: UserRepositoryBase,
) -> None:
    await process_editing(state, callback, callback_data, tg_user)


@router.callback_query(ProfileMenuCallback.filter(F.action == "save"))
async def profile_save_data(
    callback: types.CallbackQuery,
    callback_data: ProfileMenuCallback,
    state: FSMContext,
    tg_user: TelegramUser,
    user_repo: UserRepositoryBase,
) -> None:
    tg_user = await sync_profile_data(user_repo, tg_user, await state.get_data())
    msg_text = get_editing_text(tg_user=tg_user)
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=field_selector_menu())
        await callback.answer()
    else:
        await callback.answer(msg_text, reply_markup=field_selector_menu())


@router.callback_query(ProfileMenuCallback.filter(F.action == "admin_menu"))
async def profile_admin_menu(
    callback: types.CallbackQuery,
    tg_user: TelegramUser,
) -> None:
    msg_text = _("Меню администратора")
    if callback.message:
        await callback.message.edit_text(msg_text, reply_markup=admin_menu_keyboard(has_admin_rights(tg_user=tg_user)))


@router.callback_query(ProfileAdminMenuCallback.filter())
async def process_admin_callback(
    callback: types.CallbackQuery,
    callback_data: ProfileAdminMenuCallback,
    tg_user: TelegramUser,
    state: FSMContext,
    user_repo: UserRepositoryBase,
    settings: Settings,
    bot: Bot,
) -> None:
    # TODO: split by cases into different handlers
    match callback_data.action:
        case "export":
            msg_text = _("Введите время среза базы данных в формате yyyy-mm-dd HH:MM:SS (Пример: 2001-09-11 12:00:00")
            await state.set_state(ProfileAdminForm.timestamp)
            if callback.message:
                await callback.message.edit_text(
                    msg_text,
                )
            else:
                await callback.answer(
                    msg_text,
                )
            # filename = await users_table(
            #     tg_user.tg_id, user_repo.get_users(limit=10**5)
            # )

            # if callback.message:
            #     await callback.message.answer_document(
            #         types.FSInputFile(filename, filename)
            #     )
            #     await callback.message.answer(
            #         msg_text, reply_markup=admin_menu_keyboard(has_admin_rights(tg_user=tg_user))
            #     )
            #     await callback.answer()
            # else:
            #     await callback.answer(
            #         msg_text,
            #     )
        case "add_admin":
            msg_text = _("Выберите права доступа")
            admin_rights = tg_user.admin_rights.right_model
            # preselct all current rights
            preselect = ','.join(str(x) for x in admin_rights.keys())
            if callback.message:
                await callback.message.edit_text(
                    msg_text,
                    reply_markup=select_admin_rights_keyboard(admin_options=admin_rights, confirms=preselect)
                )
                await callback.answer()
            else:
                await callback.answer(
                    msg_text,
                    reply_markup=select_admin_rights_keyboard(admin_options=admin_rights, confirms=preselect)
                )

        case True:
            await callback.answer()


            # code = create_invite_code(tg_user.tg_id)
            # user_repo.create_invite_code(code, tg_user.tg_id)
            # msg_text = _(
            #     "Ссылка для добавление администратора (действительна 30 минут): \n {url}"
            # ).format(url=get_admin_invite_link(settings.bot_name, code))
            # await bot.send_message(tg_user.tg_id, msg_text)
            # await callback.answer(text=msg_text)
            # msg_text = _("Меню администратора")

            # if callback.message:
            #     await callback.message.answer(
            #         msg_text, reply_markup=admin_menu_keyboard()
            #     )
            # await callback.answer()

@router.message(ProfileAdminForm.timestamp)
async def process_admin_profile_export(
    message: types.Message,
    tg_user: TelegramUser,
    state: FSMContext,
    user_repo: UserRepositoryBase,
    settings: Settings,
    bot: Bot,
) -> None:
    # get text from message
    await state.clear()
    date_text = message.text
    # parse datetime
    try:
        timestamp = dt.datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        await message.answer(_("Неверный формат даты"))
        return
    await message.answer(_("Пожалуйста подождите..."))
    # get users
    users = user_repo.get_users_after_timestamp(timestamp)
    filename = await users_table(
                tg_user.tg_id, users
            )
    msg_text = _("Меню администратора")
    # send file to user
    await message.answer_document(
        types.FSInputFile(filename, filename)
    )
    await message.answer(
        msg_text, reply_markup=admin_menu_keyboard(has_admin_rights(tg_user=tg_user))
    )

@router.callback_query(AddAdminCallback.filter())
async def process_add_admin(
    callback: types.CallbackQuery,
    callback_data: AddAdminCallback,
    tg_user: TelegramUser,
    user_repo: UserRepositoryBase,
    settings: Settings,
    bot: Bot,
) -> None:
    confirms = callback_data.confirms.split(",") if callback_data.confirms else []
    if len(callback_data.value.split('_')) > 1:
        action, value = callback_data.value.split('_')
        if action == "rm":
            confirms.remove(value)
        else:
            confirms.append(value)
        # update keyboard
        confirms = ",".join(confirms)
        await callback.message.edit_reply_markup(
            inline_message_id=callback.inline_message_id,
            reply_markup=select_admin_rights_keyboard(
                admin_options=tg_user.admin_rights.right_model, confirms=confirms
            )
        )
    else:
        code = create_invite_code(tg_user.tg_id)
        confirms = [int(x) for x in confirms]
        user_repo.create_invite_code(code, tg_user.tg_id, confirms)
        msg_text = _(
            "Ссылка для добавление администратора (действительна 30 минут): \n {url}"
        ).format(url=get_admin_invite_link(settings.bot_name, code))
        # delete previous message
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await bot.send_message(tg_user.tg_id, msg_text)
        await callback.answer(text=msg_text)
        msg_text = _("Меню администратора")

        if callback.message:
            await callback.message.answer(
                msg_text, reply_markup=admin_menu_keyboard(has_admin_rights(tg_user=tg_user))
            )
        await callback.answer()

@router.message(Command("cancel"))
@router.message(F.text.casefold() == __("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        _("ProfileForm cancel message"),
        reply_markup=base_menu_reply_key(),
    )
    await message.answer(
        _("ProfileMenu text"),
        reply_markup=profile_menu_keyboard(),
    )


@router.message(ProfileForm.fio)
async def process_profile_form_fio(
    message: types.Message,
    state: FSMContext,
) -> None:

    # TODO: find solution to check if enetered a valid fio and detect sex from it

    if message.text and len(message.text.split(" ")) >= 2:
        fio = " ".join(map(lambda x: x.capitalize(), message.text.split(" ")))
        data = await state.get_data()
        data["tg_user"].profile.fio = fio

        await state.set_data(data)
        await state.set_state(ProfileForm.editing)
        # TODO: pass user data into message
        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        await message.answer(
            _("ProfileForm error fio state"), reply_markup=base_menu_reply_key()
        )


@router.message(ProfileForm.email)
async def process_profile_form_email(
    message: types.Message, state: FSMContext, tg_user: TelegramUser
) -> None:
    if message.text and message.text.endswith("@edu.misis.ru"):

        data = await state.get_data()
        data["tg_user"].profile.email = message.text
        await state.set_data(data)

        await state.set_state(ProfileForm.editing)
        # TODO: pass user data into message
        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        await message.answer(
            _("ProfileForm error email state"),
            reply_markup=base_menu_reply_key(),
        )


# TODO: move to utils
def check_group(group: str) -> bool:
    if len(group.split("-")) < 3:
        return False
    name = group.split("-")[0]

    if not name.startswith(("Б", "М")):
        return False

    return True


@router.message(ProfileForm.educational_group)
async def process_profile_form_group(
    message: types.Message, state: FSMContext, tg_user: TelegramUser
) -> None:

    if message.text and check_group(message.text.upper()) and tg_user.profile:
        data = await state.get_data()
        data["tg_user"].profile.educational_group = message.text.upper()
        await state.set_data(data)
        await state.set_state(ProfileForm.editing)
        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        await message.answer(
            _("ProfileForm error group state"),
            reply_markup=base_menu_reply_key(),
        )


# TODO: move to utils
def check_github(github: str) -> bool:
    if not github.startswith("http"):
        return False
    return True


@router.message(ProfileForm.portfolio_link)
async def process_profile_form_github(
    message: types.Message, state: FSMContext
) -> None:
    if message.text and check_github(message.text):
        data = await state.get_data()
        data["tg_user"].profile.portfolio_link = message.text
        await state.set_data(data)

        await state.set_state(ProfileForm.editing)
        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        await message.answer(
            _("ProfileForm error github state"),
            reply_markup=base_menu_reply_key(),
        )


# @router.message(ProfileForm.majors)
# async def process_profile_form_profession(
#     message: types.Message, state: FSMContext, tg_user: TelegramUser
# ) -> None:
#     if message.text and message.text in AVALIABLE_PROFESSIONS:
#         data = await state.get_data()
#         data["tg_user"].profile.majors = message.text.split(",")
#         await state.set_data(data)

#         await state.set_state(ProfileForm.editing)
#         msg_text = get_editing_text(data["tg_user"])
#         await message.answer(msg_text, reply_markup=field_selector_menu())

#     else:
#         await message.answer(
#             _("ProfileForm error profession state"),
#             reply_markup=base_menu_reply_key(),
#         )

@router.callback_query(MajorCallback.filter())
async def process_profile_form_profession(
    callback: types.CallbackQuery,
    callback_data: MajorCallback,
    state: FSMContext,
    tg_user: TelegramUser,
) -> None:
    data = await state.get_data()
    confirms = callback_data.confirms.split(",") if callback_data.confirms else []
    # parse actions by value in callback_data
    if len(callback_data.value.split('_')) > 1:
        action, value = callback_data.value.split('_')
        if action == "rm":
            confirms.remove(value)
        else:
            confirms.append(value)
        # update keyboard
        confirms = ",".join(confirms)
        await callback.message.edit_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=majors_keyboard(confirms))
    else:
        # extracct values from enum by name in confirms
        selections = [AVALIABLE_PROFESSIONS[major] for major in confirms]
        data["tg_user"].profile.majors = selections
        await state.set_data(data)

        await state.set_state(ProfileForm.editing)
        msg_text = get_editing_text(data["tg_user"])
        await callback.message.edit_text(msg_text, reply_markup=field_selector_menu())
        await callback.answer()

@router.message(ProfileForm.skills)
async def process_profile_form_skills(
    message: types.Message, state: FSMContext
) -> None:
    if message.text:
        data = await state.get_data()
        data["tg_user"].profile.skills = message.text.split(",")
        await state.set_data(data)

        await state.set_state(ProfileForm.editing)
        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        await message.answer(
            _("ProfileForm error skills state"),
            reply_markup=base_menu_reply_key(),
        )


@router.message(ProfileForm.external_links)
async def process_profile_external_links(
    message: types.Message,
    state: FSMContext,
) -> None:
    # TODO: check url for validation
    if message.text and all(
        map(lambda x: x.startswith("http"), message.text.split(","))
    ):
        data = await state.get_data()
        data["tg_user"].profile.external_links = message.text.split(",")
        await state.set_data(data)
        await state.set_state(ProfileForm.editing)

        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        # TODO: handle error link
        await message.answer(
            text=_("Не смог открыть ссылку: {url}").format(
                url=message.text, reply_markup=field_selector_menu()
            )
        )

@router.callback_query(MentorStatusCallback.filter())
async def process_mentor_status(
    callback: types.CallbackQuery,
    callback_data: MentorStatusCallback,
    state: FSMContext,
    tg_user: TelegramUser,
) -> None:
    data = await state.get_data()
    data["tg_user"].profile.mentor_status = callback_data.ready
    await state.set_data(data)

    await state.set_state(ProfileForm.editing)
    msg_text = get_editing_text(data["tg_user"])
    await callback.message.edit_text(msg_text, reply_markup=field_selector_menu())
    await callback.answer()

@router.message(ProfileForm.company)
async def process_profile_form_company(
    message: types.Message, state: FSMContext
) -> None:
    if message.text:
        data = await state.get_data()
        data["tg_user"].profile.company = message.text
        await state.set_data(data)

        await state.set_state(ProfileForm.editing)
        msg_text = get_editing_text(data["tg_user"])
        await message.answer(msg_text, reply_markup=field_selector_menu())
    else:
        await message.answer(
            _("ProfileForm error company state"),
            reply_markup=base_menu_reply_key(),
        )
