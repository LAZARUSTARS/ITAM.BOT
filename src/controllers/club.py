from repositories.club import ClubRepositoryBase
from repositories.club.models import ClubInfo
from repositories.users import UserRepositoryBase

class ClubController:
    def __init__(
        self, club_repo: ClubRepositoryBase, user_repo: UserRepositoryBase
    ) -> None:
        self.club_repo = club_repo
        self.user_repo = user_repo

    def get_club_info(self, club: str) -> ClubInfo | None:
        return self.club_repo.get_club_info(club)

    def is_subscribed(self, tg_id: int, club: str) -> bool:
        return self.club_repo.get_club_notifications(tg_id, club)

    def set_club_notifications(self, tg_id: int, subscribed: bool, club: str) -> None:
        self.club_repo.set_club_notifications(tg_id, subscribed, club)

    def get_club_subscribed(self, club: str) -> list[int]:
        return self.club_repo.get_club_subscribed(club)