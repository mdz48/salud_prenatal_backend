from dependency_injector.wiring import inject, Provide
from container import Container
from fastapi import APIRouter, Depends, status
from typing import List
from app.patient_diaries.infrastructure.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate, PatientDiaryResponse, ExtractedSymptomResponse, AggregatedSymptomResponse
from app.patient_diaries.infrastructure.controllers.patient_diary_controller import PatientDiaryController

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

# TODO(auth): este endpoint expone sintomas clinicos agregados sin autenticacion
# ni verificacion de que el doctor sea dueno del expediente. Hoy TODO el router
# patient-diaries esta sin auth; el gateo (RoleChecker([RoleEnum.doctor]) + ownership,
# como en medical_record_router) queda como follow-up pendiente antes de produccion.
@router.get("/medical-record/{medical_record_id}/symptoms", response_model=List[AggregatedSymptomResponse])
@inject
def get_medical_record_symptom_history(
    medical_record_id: int,
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.get_medical_record_symptom_history(medical_record_id)

@router.get("/{patient_diary_id}", response_model=PatientDiaryResponse)
@inject
def get_patient_diary(
    patient_diary_id: int,
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.get_patient_diary(patient_diary_id)

@router.get("/{patient_diary_id}/symptoms", response_model=List[ExtractedSymptomResponse])
@inject
def get_diary_symptoms(
    patient_diary_id: int,
    controller: PatientDiaryController = Depends(Provide[Container.patient_diary_controller])
):
    return controller.get_diary_symptoms(patient_diary_id)

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
