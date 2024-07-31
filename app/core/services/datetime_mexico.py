from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import settings


def get_current_datetime():
    utc_time = datetime.now(ZoneInfo("UTC"))
    mx_time = utc_time.astimezone(settings.LOCAL_TIMEZONE)
    return mx_time


def UTC_to_local(utc_datetime: datetime) -> datetime:
    local_datetime = utc_datetime - timedelta(hours=6)
    return local_datetime
