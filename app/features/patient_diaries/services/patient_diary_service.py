from sqlalchemy.orm import Session
from app.features.patient_diaries.repositories.patient_diary_repository import patient_diary_repository
from app.features.patient_diaries.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate

class PatientDiaryService:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return patient_diary_repository.get_all(db, skip=skip, limit=limit)

    def get_by_id(self, db: Session, patient_diary_id: int):
        diary = patient_diary_repository.get_by_id(db, patient_diary_id)
        if not diary:
            raise ValueError("Patient diary not found")
        return diary

    def get_by_medical_record_id(self, db: Session, medical_record_id: int):
        return patient_diary_repository.get_by_medical_record_id(db, medical_record_id)

    def create(self, db: Session, data: PatientDiaryCreate):
        diary_data = data.model_dump()
        return patient_diary_repository.create(db, diary_data)

    def update(self, db: Session, patient_diary_id: int, data: PatientDiaryUpdate):
        update_data = data.model_dump(exclude_unset=True)
        updated_diary = patient_diary_repository.update(db, patient_diary_id, update_data)
        if not updated_diary:
            raise ValueError("Patient diary not found")
        return updated_diary

    def delete(self, db: Session, patient_diary_id: int):
        deleted_diary = patient_diary_repository.delete(db, patient_diary_id)
        if not deleted_diary:
            raise ValueError("Patient diary not found") 
        return deleted_diary

patient_diary_service = PatientDiaryService()
