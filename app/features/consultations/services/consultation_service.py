from sqlalchemy.orm import Session
from app.features.consultations.repositories.consultation_repository import consultation_repository
from app.features.consultations.schemas.consultation_schema import ConsultationCreate

class ConsultationService:
    def create_consultation(self, db: Session, data: ConsultationCreate):
        consultation_data = data.model_dump()
        return consultation_repository.create(db, consultation_data)

    def get_consultations_by_medical_record(self, db: Session, medical_record_id: int):
        return consultation_repository.get_by_medical_record_id(db, medical_record_id)

consultation_service = ConsultationService()
