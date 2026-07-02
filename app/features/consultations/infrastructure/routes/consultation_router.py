from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.features.consultations.infrastructure.schemas.consultation_schema import ConsultationCreate, ConsultationResponse
from app.features.consultations.domain.entities import ConsultationEntity
from app.features.consultations.application.create_consultation_usecase import CreateConsultationUseCase
from app.features.consultations.application.get_consultations_by_medical_record_usecase import GetConsultationsByMedicalRecordUseCase

router = APIRouter(prefix="/consultations", tags=["Consultations"])

@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_consultation(
    data: ConsultationCreate, 
    usecase: CreateConsultationUseCase = Depends(Provide[Container.create_consultation_use_case])
):
    try:
        entity = ConsultationEntity(
            medical_record_id=data.medical_record_id,
            notes=data.notes,
            objective=data.objective,
            plan=data.plan,
            reported_facts=data.reported_facts
        )
        return usecase.execute(entity)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/medical-record/{medical_record_id}", response_model=List[ConsultationResponse])
@inject
def get_consultations_by_medical_record(
    medical_record_id: int, 
    usecase: GetConsultationsByMedicalRecordUseCase = Depends(Provide[Container.get_consultations_by_medical_record_use_case])
):
    return usecase.execute(medical_record_id)
