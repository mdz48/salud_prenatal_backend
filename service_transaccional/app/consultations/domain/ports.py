from typing import List, Optional, Dict
from typing import Protocol, List
from app.consultations.domain.consultation_entity import ConsultationEntity

class IConsultationRepository(Protocol):
    def get_by_medical_record_id(self, medical_record_id: int) -> List[ConsultationEntity]: ...
    def create(self, consultation_entity: ConsultationEntity) -> ConsultationEntity: ...
