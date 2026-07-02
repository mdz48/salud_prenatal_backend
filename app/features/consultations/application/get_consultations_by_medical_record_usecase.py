from typing import List
from app.features.consultations.domain.ports import IConsultationRepository
from app.features.consultations.domain.entities import ConsultationEntity

class GetConsultationsByMedicalRecordUseCase:
    def __init__(self, consultation_repo: IConsultationRepository):
        self.consultation_repo = consultation_repo

    def execute(self, medical_record_id: int) -> List[ConsultationEntity]:
        return self.consultation_repo.get_by_medical_record_id(medical_record_id)
