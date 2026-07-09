"""Validación de rangos de la bitácora con el patrón Notification (ADR-05).

Acumula todos los errores de rango en un objeto `Notification` en vez de fallar al
primero, de modo que el paciente reciba la lista completa de problemas.
"""
from __future__ import annotations

from app.core.notification import Notification
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity


class PatientDiaryValidator:
    SYSTOLIC_RANGE = (50, 300)
    DIASTOLIC_RANGE = (30, 200)
    WEIGHT_RANGE = (20.0, 300.0)

    def validate(self, diary: PatientDiaryEntity) -> Notification:
        notification = Notification()

        if diary.systolic is not None and not (
            self.SYSTOLIC_RANGE[0] <= diary.systolic <= self.SYSTOLIC_RANGE[1]
        ):
            notification.add_error(
                f"systolic fuera de rango ({self.SYSTOLIC_RANGE[0]}-{self.SYSTOLIC_RANGE[1]} mmHg)"
            )

        if diary.diastolic is not None and not (
            self.DIASTOLIC_RANGE[0] <= diary.diastolic <= self.DIASTOLIC_RANGE[1]
        ):
            notification.add_error(
                f"diastolic fuera de rango ({self.DIASTOLIC_RANGE[0]}-{self.DIASTOLIC_RANGE[1]} mmHg)"
            )

        if diary.weight_kg is not None and not (
            self.WEIGHT_RANGE[0] <= diary.weight_kg <= self.WEIGHT_RANGE[1]
        ):
            notification.add_error(
                f"weight_kg fuera de rango ({self.WEIGHT_RANGE[0]}-{self.WEIGHT_RANGE[1]} kg)"
            )

        if (
            diary.systolic is not None
            and diary.diastolic is not None
            and diary.diastolic >= diary.systolic
        ):
            notification.add_error("diastolic debe ser menor que systolic")

        return notification
