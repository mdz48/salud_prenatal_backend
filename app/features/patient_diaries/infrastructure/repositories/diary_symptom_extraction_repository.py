from typing import List, Optional
from sqlalchemy.orm import Session

from app.features.patient_diaries.domain.ports import IDiarySymptomRepository
from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.features.patient_diaries.infrastructure.models.diary_symptom_extraction_model import DiarySymptomExtraction


class DiarySymptomExtractionRepository(IDiarySymptomRepository):
    def __init__(self, db: Session):
        self.db = db

    def replace_for_diary(self, patient_diary_id: int, medical_record_id: Optional[int],
                          symptoms: List[ExtractedSymptomEntity]) -> List[ExtractedSymptomEntity]:
        # Idempotente: reprocesar una bitacora reemplaza sus extracciones previas.
        self.db.query(DiarySymptomExtraction).filter(
            DiarySymptomExtraction.patient_diary_id == patient_diary_id
        ).delete(synchronize_session=False)

        rows = [
            DiarySymptomExtraction(
                patient_diary_id=patient_diary_id,
                medical_record_id=medical_record_id,
                code=s.code,
                label=s.label,
                raw_text=s.raw_text,
                negated=s.negated,
                score=s.score,
                alarm=s.alarm,
            )
            for s in symptoms
        ]
        self.db.add_all(rows)
        self.db.commit()
        return [ExtractedSymptomEntity.model_validate(r) for r in rows]

    def get_by_diary_id(self, patient_diary_id: int) -> List[ExtractedSymptomEntity]:
        items = self.db.query(DiarySymptomExtraction).filter(
            DiarySymptomExtraction.patient_diary_id == patient_diary_id
        ).all()
        return [ExtractedSymptomEntity.model_validate(i) for i in items]

    def get_by_medical_record_id(self, medical_record_id: int) -> List[ExtractedSymptomEntity]:
        items = self.db.query(DiarySymptomExtraction).filter(
            DiarySymptomExtraction.medical_record_id == medical_record_id
        ).order_by(DiarySymptomExtraction.created_at.desc()).all()
        return [ExtractedSymptomEntity.model_validate(i) for i in items]
