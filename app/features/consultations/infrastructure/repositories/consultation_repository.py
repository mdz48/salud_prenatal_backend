from typing import List
from sqlalchemy.orm import Session
from app.features.consultations.infrastructure.models.consultation_model import Consultation
from app.features.consultations.domain.ports import IConsultationRepository
from app.features.consultations.domain.entities import ConsultationEntity

class ConsultationRepository(IConsultationRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: Consultation) -> ConsultationEntity:
        return ConsultationEntity(
            consultation_id=model.consultation_id,
            medical_record_id=model.medical_record_id,
            notes=model.notes,
            objective=model.objective,
            plan=model.plan,
            reported_facts=model.reported_facts,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def create(self, consultation_entity: ConsultationEntity) -> ConsultationEntity:
        data = consultation_entity.model_dump(exclude={"consultation_id", "created_at", "updated_at"}, exclude_unset=True)
        db_consultation = Consultation(**data)
        self.db.add(db_consultation)
        self.db.commit()
        self.db.refresh(db_consultation)
        return self._to_entity(db_consultation)

    def get_by_medical_record_id(self, medical_record_id: int) -> List[ConsultationEntity]:
        models = self.db.query(Consultation).filter(Consultation.medical_record_id == medical_record_id).all()
        return [self._to_entity(m) for m in models]
