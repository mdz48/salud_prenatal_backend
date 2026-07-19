from fastapi import HTTPException, status

from app.consultations.domain.consultation_entity import ConsultationEntity
from app.consultations.infrastructure.schemas.consultation_schema import ConsultationCreate

from app.consultations.application.create_consultation_usecase import CreateConsultationUseCase
from app.consultations.application.get_consultations_by_medical_record_usecase import GetConsultationsByMedicalRecordUseCase
from salud_prenatal_shared_core.error_handlers import internal_error

class ConsultationController:
    def __init__(
        self,
        create_consultation_usecase: CreateConsultationUseCase,
        get_consultations_by_medical_record_usecase: GetConsultationsByMedicalRecordUseCase,
    ):
        self.create_consultation_usecase = create_consultation_usecase
        self.get_consultations_by_medical_record_usecase = get_consultations_by_medical_record_usecase

    def create_consultation(self, data: ConsultationCreate):
        try:
            entity = ConsultationEntity(
                medical_record_id=data.medical_record_id,
                notes=data.notes,
                objective=data.objective,
                plan=data.plan,
                reported_facts=data.reported_facts
            )
            return self.create_consultation_usecase.execute(entity)
        except Exception as e:
            raise internal_error(e)

    def get_consultations_by_medical_record(self, medical_record_id: int):
        return self.get_consultations_by_medical_record_usecase.execute(medical_record_id)
