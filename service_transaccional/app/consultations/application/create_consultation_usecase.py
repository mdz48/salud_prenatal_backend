from app.consultations.domain.ports import IConsultationRepository
from app.consultations.domain.consultation_entity import ConsultationEntity

class CreateConsultationUseCase:
    def __init__(self, consultation_repo: IConsultationRepository):
        self.consultation_repo = consultation_repo

    def execute(self, entity: ConsultationEntity) -> ConsultationEntity:
        return self.consultation_repo.create(entity)
