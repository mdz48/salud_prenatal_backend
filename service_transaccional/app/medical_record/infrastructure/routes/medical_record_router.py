from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from fastapi import APIRouter, Depends, status
from salud_prenatal_shared_core.auth_dependencies import RoleChecker, require_active_subscription, get_current_user, Principal
from salud_prenatal_shared_core.enums import RoleEnum
from typing import List, Optional
from app.medical_record.infrastructure.schemas.medical_record_schema import (
    MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse, PatientMedicalRecordResponse, MedicalRecordSearchResult, RiskEvaluationResponse
)
from app.medical_record.infrastructure.controllers.medical_record_controller import MedicalRecordController

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])

require_doctor = RoleChecker([RoleEnum.doctor])


@router.post("/", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_medical_record(
    data: MedicalRecordCreate,
    current_user: Principal = Depends(get_current_user),
):
    controller = Container.medical_record_controller()
    return controller.create_medical_record(data)


@router.get("/search", response_model=List[MedicalRecordSearchResult], status_code=status.HTTP_200_OK)
@close_db_after(Container)
def search_medical_records(
    doctor_id: int,
    name: Optional[str] = None,
    last_name: Optional[str] = None,
    current_user: Principal = Depends(get_current_user),
):
    controller = Container.medical_record_controller()
    return controller.search_medical_records(doctor_id=doctor_id, name=name, last_name=last_name)


@router.get("/patient/{patient_id}", response_model=PatientMedicalRecordResponse, status_code=status.HTTP_200_OK)
@close_db_after(Container)
def get_patient_medical_record(
    patient_id: int,
    doctor_id: int,
    current_user: Principal = Depends(get_current_user),
):
    controller = Container.medical_record_controller()
    return controller.get_patient_medical_record(patient_id, doctor_id)


@router.post("/{medical_record_id}/risk-evaluation", response_model=RiskEvaluationResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def evaluate_risk(
    medical_record_id: int,
    current_user = Depends(require_doctor),
    _subscription = Depends(require_active_subscription),
):
    controller = Container.medical_record_controller()
    return controller.evaluate_risk(medical_record_id)


@router.put("/{medical_record_id}", response_model=MedicalRecordResponse, status_code=status.HTTP_200_OK)
@close_db_after(Container)
def update_medical_record(
    medical_record_id: int,
    data: MedicalRecordUpdate,
    current_user = Depends(require_doctor),
    _subscription = Depends(require_active_subscription),
):
    controller = Container.medical_record_controller()
    return controller.update_medical_record(medical_record_id, data)
