from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from app.features.users.infrastructure.schemas.patient_schema import PatientRegistration, PatientResponse, PatientDashboardResponse
from app.features.users.infrastructure.schemas.invitation_code_schema import RedeemCodeRequest
from app.features.users.infrastructure.controllers.patient_controller import PatientController


router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/{patient_id}/dashboard", response_model=PatientDashboardResponse, status_code=status.HTTP_200_OK)
@inject
def get_patient_dashboard(patient_id: int, controller: PatientController = Depends(Provide[Container.patient_controller])):
    return controller.get_patient_dashboard(patient_id=patient_id)

@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
@inject
def register_patient(data: PatientRegistration, controller: PatientController = Depends(Provide[Container.patient_controller])):
    return controller.register_patient(data=data)

@router.post("/{patient_id}/redeem-code", response_model=PatientResponse, status_code=status.HTTP_200_OK)
@inject
def redeem_code(patient_id: int, data: RedeemCodeRequest, controller: PatientController = Depends(Provide[Container.patient_controller])):
    return controller.redeem_code(patient_id=patient_id, data=data)
