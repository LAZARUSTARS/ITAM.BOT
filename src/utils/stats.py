import datetime as dt
import aiofiles
import csv
from repositories.users.models import TelegramUser

# TODO: create stats service
async def users_table(admin_id: int, users: list[TelegramUser]):
    filename = f"{admin_id}_{dt.datetime.now().isoformat()}.csv"
    fieldnames = [
        "timestamp",
        "tg_id",
        "first_name",
        "last_name",
        "username",
        "language_code",
        "is_premium",
        "fio",
        "email",
        "educational_group",
        "portfolio_link",
        "majors",
        "external_links",
        "skills",
        "mentor_status",
        "company",
    ]

    async with aiofiles.open(filename, "w", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames,
        )
        await writer.writeheader()
        for u in users:
            data = u.model_dump()
            data.update(data.pop("profile"))
            data.pop("is_admin")
            data.pop("admin_rights")
            data
            await writer.writerow(data)
    return filename
