from sqlalchemy.orm import Session
from app.features.patient_diaries.models.patient_diaries_model import PatientDiary

class PatientDiaryRepository:
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(PatientDiary).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, patient_diary_id: int):
        return db.query(PatientDiary).filter(PatientDiary.patient_diary_id == patient_diary_id).first()

    def get_by_medical_record_id(self, db: Session, medical_record_id: int):
        return db.query(PatientDiary).filter(PatientDiary.medical_record_id == medical_record_id).all()

    def create(self, db: Session, diary_data: dict, commit: bool = True):
        db_diary = PatientDiary(**diary_data)
        db.add(db_diary)
        if commit:
            db.commit()
            db.refresh(db_diary)
        else:
            db.flush()
        return db_diary

    def update(self, db: Session, patient_diary_id: int, update_data: dict, commit: bool = True):
        db_diary = self.get_by_id(db, patient_diary_id)
        if db_diary:
            for key, value in update_data.items():
                if value is not None:
                    setattr(db_diary, key, value)
            if commit:
                db.commit()
                db.refresh(db_diary)
            else:
                db.flush()
        return db_diary

    def delete(self, db: Session, patient_diary_id: int, commit: bool = True):
        db_diary = self.get_by_id(db, patient_diary_id)
        if db_diary:
            db.delete(db_diary)
            if commit:
                db.commit()
        return db_diary

patient_diary_repository = PatientDiaryRepository()
