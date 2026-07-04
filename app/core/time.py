from datetime import datetime, timezone, timedelta

CDMX_TZ = timezone(timedelta(hours=-6))

def now_cdmx() -> datetime:
    return datetime.now(CDMX_TZ)
