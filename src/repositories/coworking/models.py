from dataclasses import dataclass
import typing as tp
import datetime as dt

COWORKING_STATUS = tp.Literal["open", "close"]
COWORKING_ACTIONS = tp.Literal["open", "close", "gain_control"]


@dataclass
class CoworkingStatus:
    """Статус коворкинга

    Attributes
    ----------
    responsible_mention : str
        упоминание ответственного за коворкинг
    status : COWORKING_STATUS
        open/close
    duration: int
        время, на которое закрыт коворкинг (в минутах)
    time: datetime.datetime
        время, когда был установлен статус
    """

    OPEN = "open"
    CLOSE = "close"
    GAIN_CONTROL = "gain_control"

    responsible_mention: str
    status: tp.Annotated[str, COWORKING_STATUS]
    duration: tp.Optional[int]
    time: dt.datetime
