from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from app.features.medical_record.infrastructure.schemas.medical_record_schema import MedicalRecordCreate, MedicalRecordResponse, PatientMedicalRecordResponse
from app.features.medical_record.application.create_medical_record_usecase import CreateMedicalRecordUseCase
from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase
from app.features.medical_record.domain.entities import MedicalRecordEntity

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])




@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_medical_record(
    data: MedicalRecordCreate,
    usecase: CreateMedicalRecordUseCase = Depends(Provide[Container.create_medical_record_use_case])
):
    try:
        # Map schema to entity
        entity_data = MedicalRecordEntity(**data.model_dump())
        result_entity = usecase.execute(data=entity_data)
        return result_entity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the medical record.")

@router.get("/patient/{patient_id}", response_model=PatientMedicalRecordResponse, status_code=status.HTTP_200_OK)
@inject
def get_patient_medical_record(
    patient_id: int, 
    doctor_id: int, 
    usecase: GetPatientMedicalRecordUseCase = Depends(Provide[Container.get_patient_medical_record_use_case])
):
    try:
        return usecase.execute(patient_id=patient_id, doctor_id=doctor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the medical record.")
