from typing import List

from app.patient_diaries.domain.notification import Notification
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

WEIGHT_MIN_KG = 20.0
WEIGHT_MAX_KG = 300.0
SYSTOLIC_MIN_MMHG = 40
SYSTOLIC_MAX_MMHG = 300
DIASTOLIC_MIN_MMHG = 20
DIASTOLIC_MAX_MMHG = 200


def validate_diary_measurements(entity: PatientDiaryEntity) -> Notification:
    notification = Notification()

    if entity.weight_kg is not None and not (WEIGHT_MIN_KG <= entity.weight_kg <= WEIGHT_MAX_KG):
        notification.add_error(
            f"El peso debe estar entre {WEIGHT_MIN_KG:g} y {WEIGHT_MAX_KG:g} kg."
        )

    if entity.systolic is not None and not (SYSTOLIC_MIN_MMHG <= entity.systolic <= SYSTOLIC_MAX_MMHG):
        notification.add_error(
            f"La presión sistólica debe estar entre {SYSTOLIC_MIN_MMHG} y {SYSTOLIC_MAX_MMHG} mmHg."
        )

    if entity.diastolic is not None and not (DIASTOLIC_MIN_MMHG <= entity.diastolic <= DIASTOLIC_MAX_MMHG):
        notification.add_error(
            f"La presión diastólica debe estar entre {DIASTOLIC_MIN_MMHG} y {DIASTOLIC_MAX_MMHG} mmHg."
        )

    if (
        entity.systolic is not None
        and entity.diastolic is not None
        and entity.systolic <= entity.diastolic
    ):
        notification.add_error(
            "La presión sistólica debe ser mayor que la diastólica."
        )

    return notification


class PatientDiaryValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("; ".join(errors))
