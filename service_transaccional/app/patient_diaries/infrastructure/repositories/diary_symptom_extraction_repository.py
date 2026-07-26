from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.patient_diaries.domain.ports import IDiarySymptomRepository
from app.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.patient_diaries.domain.body_zone_entity import BodyZoneEntity
from app.patient_diaries.domain.symptom_extraction_result_entity import SymptomExtractionResult
from app.patient_diaries.infrastructure.models.diary_symptom_extraction_model import DiarySymptomExtraction
from app.patient_diaries.infrastructure.models.diary_body_zone_model import DiaryBodyZone


class DiarySymptomExtractionRepository(IDiarySymptomRepository):
    def __init__(self, db: Session):
        self.db = db

    def replace_for_diary(self, patient_diary_id: int, medical_record_id: Optional[int],
                          result: SymptomExtractionResult) -> List[ExtractedSymptomEntity]:
        # Idempotente: reprocesar una bitacora reemplaza sus extracciones previas.
        self.db.query(DiarySymptomExtraction).filter(
            DiarySymptomExtraction.patient_diary_id == patient_diary_id
        ).delete(synchronize_session=False)
        self.db.query(DiaryBodyZone).filter(
            DiaryBodyZone.patient_diary_id == patient_diary_id
        ).delete(synchronize_session=False)

        symptom_rows = [
            DiarySymptomExtraction(
                patient_diary_id=patient_diary_id,
                medical_record_id=medical_record_id,
                code=s.code,
                label=s.label,
                raw_text=s.raw_text,
                negated=s.negated,
                score=s.score,
                alarm=s.alarm,
                zones=[z.model_dump(exclude={"zone_id", "model_version"}) for z in s.zones],
                model_version=result.model_version,
            )
            for s in result.symptoms
        ]
        zone_rows = [
            DiaryBodyZone(
                patient_diary_id=patient_diary_id,
                medical_record_id=medical_record_id,
                code=z.code,
                label=z.label,
                raw_text=z.raw_text,
                negated=z.negated,
                score=z.score,
                model_version=result.model_version,
            )
            for z in result.body_zones
        ]
        self.db.add_all(symptom_rows)
        self.db.add_all(zone_rows)
        self.db.commit()
        return [ExtractedSymptomEntity.model_validate(r) for r in symptom_rows]

    def get_by_diary_id(self, patient_diary_id: int) -> List[ExtractedSymptomEntity]:
        items = self.db.query(DiarySymptomExtraction).filter(
            DiarySymptomExtraction.patient_diary_id == patient_diary_id
        ).all()
        return [ExtractedSymptomEntity.model_validate(i) for i in items]

    def get_by_medical_record_id(self, medical_record_id: int, since: Optional[datetime] = None) -> List[ExtractedSymptomEntity]:
        query = self.db.query(DiarySymptomExtraction).filter(
            DiarySymptomExtraction.medical_record_id == medical_record_id
        )
        if since is not None:
            query = query.filter(DiarySymptomExtraction.created_at > since)
        items = query.order_by(DiarySymptomExtraction.created_at.desc()).all()
        return [ExtractedSymptomEntity.model_validate(i) for i in items]

    def get_body_zones_by_diary_id(self, patient_diary_id: int) -> List[BodyZoneEntity]:
        items = self.db.query(DiaryBodyZone).filter(
            DiaryBodyZone.patient_diary_id == patient_diary_id
        ).all()
        return [BodyZoneEntity.model_validate(i) for i in items]
