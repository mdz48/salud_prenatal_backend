from datetime import date, datetime, timezone, timedelta

# Mexico abolio el horario de verano en 2022; UTC-6 fijo es correcto todo el año.
CDMX_TZ = timezone(timedelta(hours=-6))

def now_cdmx() -> datetime:
    return datetime.now(CDMX_TZ)

def today_cdmx() -> date:
    return datetime.now(CDMX_TZ).date()
