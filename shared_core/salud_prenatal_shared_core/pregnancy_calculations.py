"""Calculos de embarazo/edad compartidos por features (users, medical_record).

Funciones puras: reciben la fecha de referencia explicita (default: hoy en CDMX)
para que sean deterministas en tests.
"""
from datetime import date
from typing import Optional

from salud_prenatal_shared_core.time import today_cdmx


def gestational_weeks(
    last_menstrual_period: Optional[date],
    weeks_at_registration: Optional[int],
    today: Optional[date] = None,
) -> Optional[int]:
    if last_menstrual_period:
        reference = today or today_cdmx()
        return (reference - last_menstrual_period).days // 7
    return weeks_at_registration


def age_years(birthdate: Optional[date], today: Optional[date] = None) -> Optional[int]:
    if not birthdate:
        return None
    reference = today or today_cdmx()
    return (
        reference.year
        - birthdate.year
        - ((reference.month, reference.day) < (birthdate.month, birthdate.day))
    )
