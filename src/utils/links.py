from repositories.users.models import TelegramUser


def get_admin_invite_link(bot_name: str, token: str) -> str:
    return f"https://t.me/{bot_name}?start={token}"


def get_user_mention(tg_user: TelegramUser) -> str:
    return (
        f"@{tg_user.username}"
        if tg_user.username
        else f'<a href="tg://user?id={tg_user.tg_id}">{tg_user.first_name}</a>'
    )
