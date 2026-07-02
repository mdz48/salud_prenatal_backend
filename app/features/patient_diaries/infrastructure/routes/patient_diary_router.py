from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.features.patient_diaries.infrastructure.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate, PatientDiaryResponse
from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.features.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.features.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.features.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.features.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.features.patient_diaries.domain.entities import PatientDiaryEntity

router = APIRouter(prefix="/patient-diaries", tags=["Patient Diaries"])
@router.post("/", response_model=PatientDiaryResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_patient_diary(
    data: PatientDiaryCreate, 
    usecase: CreatePatientDiaryUseCase = Depends(Provide[Container.create_patient_diary_use_case])
):
    try:
        entity = PatientDiaryEntity(**data.model_dump())
        return usecase.execute(data=entity)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[PatientDiaryResponse])
@inject
def get_all_patient_diaries(
    skip: int = 0, 
    limit: int = 100, 
    usecase: GetAllPatientDiariesUseCase = Depends(Provide[Container.get_all_patient_diaries_use_case])
):
    return usecase.execute(skip=skip, limit=limit)

@router.get("/medical-record/{medical_record_id}", response_model=List[PatientDiaryResponse])
@inject
def get_diaries_by_medical_record(
    medical_record_id: int, 
    usecase: GetDiariesByMedicalRecordUseCase = Depends(Provide[Container.get_diaries_by_medical_record_use_case])
):
    return usecase.execute(medical_record_id=medical_record_id)

@router.get("/{patient_diary_id}", response_model=PatientDiaryResponse)
@inject
def get_patient_diary(
    patient_diary_id: int, 
    usecase: GetPatientDiaryByIdUseCase = Depends(Provide[Container.get_patient_diary_by_id_use_case])
):
    try:
        return usecase.execute(patient_diary_id=patient_diary_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{patient_diary_id}", response_model=PatientDiaryResponse)
@inject
def update_patient_diary(
    patient_diary_id: int, 
    data: PatientDiaryUpdate, 
    usecase: UpdatePatientDiaryUseCase = Depends(Provide[Container.update_patient_diary_use_case])
):
    try:
        entity = PatientDiaryEntity(**data.model_dump(exclude_unset=True))
        return usecase.execute(patient_diary_id=patient_diary_id, data=entity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{patient_diary_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_patient_diary(
    patient_diary_id: int, 
    usecase: DeletePatientDiaryUseCase = Depends(Provide[Container.delete_patient_diary_use_case])
):
    try:
        usecase.execute(patient_diary_id=patient_diary_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
