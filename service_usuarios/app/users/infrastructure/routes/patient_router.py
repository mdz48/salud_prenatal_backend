from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from fastapi import APIRouter, Depends, status
from typing import List, Optional
from app.users.infrastructure.schemas.patient_schema import PatientRegistration, PatientResponse, PatientDashboardResponse
from app.users.infrastructure.schemas.invitation_code_schema import RedeemCodeRequest
from app.users.infrastructure.schemas.unlink_request_schema import UnlinkRequestCreate, UnlinkRequestResponse
from app.users.infrastructure.controllers.patient_controller import PatientController

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/{patient_id}/dashboard", response_model=PatientDashboardResponse, status_code=status.HTTP_200_OK)
@close_db_after(Container)
def get_patient_dashboard(patient_id: int):
    controller = Container.patient_controller()
    return controller.get_patient_dashboard(patient_id=patient_id)


@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def register_patient(data: PatientRegistration):
    controller = Container.patient_controller()
    return controller.register_patient(data=data)


@router.post("/{patient_id}/redeem-code", response_model=PatientResponse, status_code=status.HTTP_200_OK)
@close_db_after(Container)
def redeem_code(patient_id: int, data: RedeemCodeRequest):
    controller = Container.patient_controller()
    return controller.redeem_code(patient_id=patient_id, data=data)


@router.post("/{patient_id}/unlink-requests", response_model=UnlinkRequestResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_unlink_request(patient_id: int, data: UnlinkRequestCreate):
    controller = Container.patient_controller()
    return controller.create_unlink_request(patient_id=patient_id, data=data)


@router.get("/{patient_id}/unlink-requests", response_model=List[UnlinkRequestResponse], status_code=status.HTTP_200_OK)
@close_db_after(Container)
def list_unlink_requests(patient_id: int, status: Optional[str] = None):
    controller = Container.patient_controller()
    return controller.list_unlink_requests(patient_id=patient_id, status_filter=status)


@router.delete("/{patient_id}/unlink-requests/{request_id}", response_model=UnlinkRequestResponse, status_code=status.HTTP_200_OK)
@close_db_after(Container)
def cancel_unlink_request(patient_id: int, request_id: int):
    controller = Container.patient_controller()
    return controller.cancel_unlink_request(patient_id=patient_id, request_id=request_id)
