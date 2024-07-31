from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings


def get_current_datetime():
    utc_time = datetime.now(ZoneInfo("UTC"))
    mx_time = utc_time.astimezone(settings.LOCAL_TIMEZONE)
    return mx_time


def UTC_to_local(utc_datetime: datetime) -> datetime:
    utc_datetime = utc_datetime.astimezone(ZoneInfo("UTC"))

    # Convert to local timezone
    local_datetime = utc_datetime.astimezone(settings.LOCAL_TIMEZONE)
    return local_datetime
