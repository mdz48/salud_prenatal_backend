from sqlalchemy.orm import Session
from app.features.consultations.models.consultation_model import Consultation
from app.features.medical_record.models.medical_record_model import MedicalRecord

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
                 .join(MedicalRecord, Consultation.patient_id == MedicalRecord.patient_id)\
                 .filter(MedicalRecord.medical_record_id == medical_record_id)\
                 .all()

consultation_repository = ConsultationRepository()
