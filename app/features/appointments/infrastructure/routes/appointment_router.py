from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from typing import List

from app.features.appointments.infrastructure.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.features.appointments.infrastructure.controllers.appointment_controller import AppointmentController

from app.core.enums import RoleEnum
from app.core.dependencies import RoleChecker, require_active_subscription
from app.features.users.domain.user_entity import UserEntity

router = APIRouter(prefix="/appointments", tags=["Appointments"])

allow_doctor_or_receptionist = RoleChecker([RoleEnum.doctor, RoleEnum.recepcionist])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_appointment(
    data: AppointmentCreate,
    controller: AppointmentController = Depends(Provide[Container.appointment_controller]),
    current_user: UserEntity = Depends(allow_doctor_or_receptionist),
    _subscription: UserEntity = Depends(require_active_subscription)
):
    return controller.create_appointment(data)

@router.get("/{appointment_id}", response_model=AppointmentResponse)
@inject
def get_appointment(
    appointment_id: int, 
    controller: AppointmentController = Depends(Provide[Container.appointment_controller])
):
    return controller.get_appointment(appointment_id)

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
@inject
def get_appointments_by_patient(
    patient_id: int, 
    controller: AppointmentController = Depends(Provide[Container.appointment_controller])
):
    return controller.get_appointments_by_patient(patient_id)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
@inject
def get_appointments_by_doctor(
    doctor_id: int, 
    controller: AppointmentController = Depends(Provide[Container.appointment_controller])
):
    return controller.get_appointments_by_doctor(doctor_id)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
@inject
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    controller: AppointmentController = Depends(Provide[Container.appointment_controller]),
    current_user: UserEntity = Depends(allow_doctor_or_receptionist),
    _subscription: UserEntity = Depends(require_active_subscription)
):
    return controller.update_appointment(appointment_id, data)

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_appointment(
    appointment_id: int,
    controller: AppointmentController = Depends(Provide[Container.appointment_controller]),
    current_user: UserEntity = Depends(allow_doctor_or_receptionist),
    _subscription: UserEntity = Depends(require_active_subscription)
):
    return controller.delete_appointment(appointment_id)
