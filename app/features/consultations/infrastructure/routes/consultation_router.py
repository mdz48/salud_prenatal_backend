from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from typing import List

from app.features.consultations.infrastructure.schemas.consultation_schema import ConsultationCreate, ConsultationResponse
from app.features.consultations.infrastructure.controllers.consultation_controller import ConsultationController

router = APIRouter(prefix="/consultations", tags=["Consultations"])

@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_consultation(
    data: ConsultationCreate, 
    controller: ConsultationController = Depends(Provide[Container.consultation_controller])
):
    return controller.create_consultation(data)

@router.get("/medical-record/{medical_record_id}", response_model=List[ConsultationResponse])
@inject
def get_consultations_by_medical_record(
    medical_record_id: int, 
    controller: ConsultationController = Depends(Provide[Container.consultation_controller])
):
    return controller.get_consultations_by_medical_record(medical_record_id)
