from sqlalchemy.orm import Session
from app.features.consultations.models.consultation_model import Consultation

class ConsultationRepository:
    def create(self, db: Session, consultation_data: dict, commit: bool = True):
        db_consultation = Consultation(**consultation_data)
        db.add(db_consultation)
        if commit:
            db.commit()
            db.refresh(db_consultation)
        else:
            db.flush()
        return db_consultation

    def get_by_medical_record_id(self, db: Session, medical_record_id: int):
        return db.query(Consultation)\
                 .filter(Consultation.medical_record_id == medical_record_id)\
                 .all()

consultation_repository = ConsultationRepository()
