from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_datetime():
    utc_time = datetime.now(ZoneInfo("UTC"))
    return utc_time.astimezone(ZoneInfo("America/Mexico_City"))
