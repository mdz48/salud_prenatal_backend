from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from fastapi import APIRouter, Depends, status
from typing import List

from app.consultations.infrastructure.schemas.consultation_schema import ConsultationCreate, ConsultationResponse
from app.consultations.infrastructure.controllers.consultation_controller import ConsultationController

router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_consultation(
    data: ConsultationCreate, 
):
    controller = Container.consultation_controller()
    return controller.create_consultation(data)


@router.get("/medical-record/{medical_record_id}", response_model=List[ConsultationResponse])
@close_db_after(Container)
def get_consultations_by_medical_record(
    medical_record_id: int, 
):
    controller = Container.consultation_controller()
    return controller.get_consultations_by_medical_record(medical_record_id)
