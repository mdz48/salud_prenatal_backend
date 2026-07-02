from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from typing import List
from app.features.patient_diaries.infrastructure.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate, PatientDiaryResponse
from app.features.patient_diaries.infrastructure.controllers.patient_diary_controller import PatientDiaryController

router = APIRouter(prefix="/patient-diaries", tags=["Patient Diaries"])

@router.post("/", response_model=PatientDiaryResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_patient_diary(
    data: PatientDiaryCreate, 
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.create_patient_diary(data)

@router.get("/", response_model=List[PatientDiaryResponse])
@inject
def get_all_patient_diaries(
    skip: int = 0, 
    limit: int = 100, 
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.get_all_patient_diaries(skip=skip, limit=limit)

@router.get("/medical-record/{medical_record_id}", response_model=List[PatientDiaryResponse])
@inject
def get_diaries_by_medical_record(
    medical_record_id: int, 
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.get_diaries_by_medical_record(medical_record_id)

@router.get("/{patient_diary_id}", response_model=PatientDiaryResponse)
@inject
def get_patient_diary(
    patient_diary_id: int, 
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.get_patient_diary(patient_diary_id)

@router.put("/{patient_diary_id}", response_model=PatientDiaryResponse)
@inject
def update_patient_diary(
    patient_diary_id: int, 
    data: PatientDiaryUpdate, 
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.update_patient_diary(patient_diary_id, data)

@router.delete("/{patient_diary_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_patient_diary(
    patient_diary_id: int, 
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    controller.delete_patient_diary(patient_diary_id)
