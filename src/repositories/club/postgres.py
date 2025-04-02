import psycopg2
import typing as tp
import datetime as dt
from .base import ClubRepositoryBase
from .models import ClubInfo, ButtonLinks
import psycopg2.extensions

class ClubRepositoryPostgres(ClubRepositoryBase):
    def __init__(self, connection: psycopg2.extensions.connection) -> None:
        self.conn = connection

    def get_club_info(self, club: str) -> ClubInfo | None:
        cur = self.conn.cursor()
        cur.execute(
            """
            select id, name, description, chat_link from clubs where name = %s;
            """,
            (club,),
        )
        result = cur.fetchone()
        # get addtionall links from other table by id of club
        if result is None:
            cur.close()
            return None
        club_id, key_name, description, link = result
        cur.execute(
            """
            select button_name, link from clubs_additional_links where club_id = %s;
            """,
            (club_id,),
        )
        additional_links = cur.fetchall()
        cur.close()
        additional_links = [ButtonLinks(row[0], row[1]) for row in additional_links]
        return ClubInfo(key_name, description, link, additional_links)


    def set_club_notifications(self, tg_id: int, subscribed: bool, club: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            update subscriptions set {} = %s where id = %s;
            """.format(club),
            (
                subscribed,
                tg_id,
            ),
        )
        self.conn.commit()
        cur.close()

    def get_club_notifications(self, tg_id: int, club: str) -> bool:
        cur = self.conn.cursor()
        cur.execute(
            """
            select {} from subscriptions where id = %s;
            """.format(club),
            (tg_id,),
        )
        result = cur.fetchone()
        if result is None:
            raise ValueError
        cur.close()
        return result[0]

    def get_club_subscribed(self, club: str) -> list[int]:
        cur = self.conn.cursor()
        cur.execute(
            """
            select id from subscriptions where %s = true;
            """,
            (club,),
        )
        result = cur.fetchall()
        cur.close()
        return [row[0] for row in result]