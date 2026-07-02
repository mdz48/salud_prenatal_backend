from sqlalchemy.orm import Session
from app.features.medical_record.infrastructure.models.medical_record_model import MedicalRecord
from app.features.medical_record.domain.ports import IMedicalRecordRepository
from app.features.medical_record.domain.entities import MedicalRecordEntity

class MedicalRecordRepository(IMedicalRecordRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_patient_and_doctor(self, patient_id: int, doctor_id: int) -> MedicalRecordEntity | None:
        db_obj = self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id,
            MedicalRecord.doctor_id == doctor_id
        ).first()
        if db_obj:
            return MedicalRecordEntity.model_validate(db_obj)
        return None

    def create(self, data: MedicalRecordEntity) -> MedicalRecordEntity:
        db_obj = MedicalRecord(**data.model_dump(exclude_unset=True, exclude={"medical_record_id"}))
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return MedicalRecordEntity.model_validate(db_obj)
