from dependency_injector.wiring import inject, Provide
from container import Container
from fastapi import APIRouter, Depends, status
from app.users.infrastructure.schemas.doctor_schema import DoctorRegistration, DoctorResponse, DoctorDetailResponse, DoctorDashboardResponse
from app.users.infrastructure.schemas.patient_schema import PatientResponse, PatientSearchResult
from app.users.infrastructure.schemas.invitation_code_schema import InvitationCodeResponse
from app.users.infrastructure.schemas.receptionist_schema import ReceptionistCreate, ReceptionistResponse, ReceptionistDetailResponse, ReceptionistDashboardResponse
from typing import List, Optional

from app.users.infrastructure.controllers.doctor_controller import DoctorController


router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/receptionists/{receptionist_id}", response_model=ReceptionistDetailResponse, status_code=status.HTTP_200_OK)
@inject
def get_receptionist_by_id(receptionist_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.get_receptionist_by_id(receptionist_id=receptionist_id)

@router.get("/receptionists/{receptionist_id}/dashboard", response_model=ReceptionistDashboardResponse, status_code=status.HTTP_200_OK)
@inject
def get_receptionist_dashboard(receptionist_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.get_receptionist_dashboard(receptionist_id=receptionist_id)

@router.get("/{doctor_id}/dashboard", response_model=DoctorDashboardResponse, status_code=status.HTTP_200_OK)
@inject
def get_doctor_dashboard(doctor_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.get_doctor_dashboard(doctor_id=doctor_id)

@router.get("/{doctor_id}", response_model=DoctorDetailResponse, status_code=status.HTTP_200_OK)
@inject
def get_doctor_by_id(doctor_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.get_doctor_by_id(doctor_id=doctor_id)

@router.post("/{doctor_id}/receptionists", response_model=ReceptionistResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_receptionist(doctor_id: int, data: ReceptionistCreate, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.create_receptionist(doctor_id=doctor_id, data=data)

@router.get("/{doctor_id}/receptionists", response_model=List[ReceptionistResponse], status_code=status.HTTP_200_OK)
@inject
def get_receptionists_by_doctor(doctor_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.get_receptionists_by_doctor(doctor_id=doctor_id)

@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
@inject
def register_doctor(data: DoctorRegistration, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.register_doctor(data=data)

@router.get("/{doctor_id}/patients/search", response_model=List[PatientSearchResult], status_code=status.HTTP_200_OK)
@inject
def search_patients(doctor_id: int, name: Optional[str] = None, last_name: Optional[str] = None, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.search_patients(doctor_id=doctor_id, name=name, last_name=last_name)

@router.get("/{doctor_id}/patients", response_model=List[PatientResponse], status_code=status.HTTP_200_OK)
@inject
def get_patients_by_doctor(doctor_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.get_patients_by_doctor(doctor_id=doctor_id)

@router.post("/{doctor_id}/invitation-code", response_model=InvitationCodeResponse, status_code=status.HTTP_201_CREATED)
@inject
def generate_invitation_code(doctor_id: int, controller: DoctorController = Depends(Provide[Container.doctor_controller])):
    return controller.generate_invitation_code(doctor_id=doctor_id)
