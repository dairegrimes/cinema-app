from datetime import datetime
from zoneinfo import ZoneInfo


def get_datetime(year, month, day, hour, minute) -> datetime:
    irish_tz = ZoneInfo("Europe/Dublin")
    return datetime(year, month, day, hour, minute, tzinfo=irish_tz)
