from typing import Optional

from app.medical_record.domain.ports import ILatestDiaryPort
from app.medical_record.domain.dtos import LatestDiary
from app.patient_diaries.infrastructure.repositories.patient_diary_repository import PatientDiaryRepository


class LatestDiaryAdapter(ILatestDiaryPort):
    """Adapter que cruza la bitacora mas reciente desde `patient_diaries` hacia el
    expediente. Delega en el repositorio del otro feature (que hace la consulta
    ordenada + limit 1) y mapea su entidad al DTO local `LatestDiary`."""

    def __init__(self, patient_diary_repository: PatientDiaryRepository):
        self.patient_diary_repository = patient_diary_repository

    def get_latest_diary_for_medical_record(self, medical_record_id: int) -> Optional[LatestDiary]:
        diary = self.patient_diary_repository.get_latest_by_medical_record_id(medical_record_id)
        if not diary:
            return None
        return LatestDiary(
            created_at=diary.created_at,
            systolic=diary.systolic,
            diastolic=diary.diastolic,
            weight_kg=diary.weight_kg,
            weight_gain=diary.weight_gain,
        )
