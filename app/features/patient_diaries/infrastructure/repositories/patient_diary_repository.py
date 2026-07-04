from typing import List, Optional
from sqlalchemy.orm import Session
from app.features.patient_diaries.infrastructure.models.patient_diaries_model import PatientDiary
from app.features.patient_diaries.domain.ports import IPatientDiaryRepository
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from typing import List

class PatientDiaryRepository(IPatientDiaryRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[PatientDiaryEntity]:
        db_items = self.db.query(PatientDiary).offset(skip).limit(limit).all()
        return [PatientDiaryEntity.model_validate(item) for item in db_items]

    def get_by_id(self, patient_diary_id: int) -> Optional[PatientDiaryEntity]:
        db_obj = self.db.query(PatientDiary).filter(PatientDiary.patient_diary_id == patient_diary_id).first()
        if db_obj:
            return PatientDiaryEntity.model_validate(db_obj)
        return None

    def get_by_medical_record_id(self, medical_record_id: int) -> List[PatientDiaryEntity]:
        db_items = self.db.query(PatientDiary).filter(PatientDiary.medical_record_id == medical_record_id).all()
        return [PatientDiaryEntity.model_validate(item) for item in db_items]

    def create(self, diary_data: PatientDiaryEntity) -> PatientDiaryEntity:
        db_diary = PatientDiary(**diary_data.model_dump(exclude_unset=True, exclude={"patient_diary_id", "created_at", "updated_at", "weight_gain"}))
        self.db.add(db_diary)
        self.db.commit()
        self.db.refresh(db_diary)
        return PatientDiaryEntity.model_validate(db_diary)

    def update(self, patient_diary_id: int, update_data: PatientDiaryEntity) -> Optional[PatientDiaryEntity]:
        db_diary = self.db.query(PatientDiary).filter(PatientDiary.patient_diary_id == patient_diary_id).first()
        if db_diary:
            update_dict = update_data.model_dump(exclude_unset=True, exclude={"patient_diary_id", "created_at", "updated_at", "medical_record_id", "weight_gain"})
            for key, value in update_dict.items():
                if value is not None:
                    setattr(db_diary, key, value)
            self.db.commit()
            self.db.refresh(db_diary)
            return PatientDiaryEntity.model_validate(db_diary)
        return None

    def delete(self, patient_diary_id: int) -> bool:
        db_diary = self.db.query(PatientDiary).filter(PatientDiary.patient_diary_id == patient_diary_id).first()
        if db_diary:
            self.db.delete(db_diary)
            self.db.commit()
            return True
        return False
