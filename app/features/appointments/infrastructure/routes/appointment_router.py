from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.features.appointments.infrastructure.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.features.appointments.domain.entities import AppointmentEntity

from app.features.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.features.appointments.application.get_appointment_usecase import GetAppointmentUseCase
from app.features.appointments.application.get_appointments_by_patient_usecase import GetAppointmentsByPatientUseCase
from app.features.appointments.application.get_appointments_by_doctor_usecase import GetAppointmentsByDoctorUseCase
from app.features.appointments.application.update_appointment_usecase import UpdateAppointmentUseCase
from app.features.appointments.application.delete_appointment_usecase import DeleteAppointmentUseCase

from app.features.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.features.appointments.application.get_appointment_usecase import GetAppointmentUseCase
from app.features.appointments.application.get_appointments_by_patient_usecase import GetAppointmentsByPatientUseCase
from app.features.appointments.application.get_appointments_by_doctor_usecase import GetAppointmentsByDoctorUseCase
from app.features.appointments.application.update_appointment_usecase import UpdateAppointmentUseCase
from app.features.appointments.application.delete_appointment_usecase import DeleteAppointmentUseCase

from app.core.enums import RoleEnum
from app.core.dependencies import RoleChecker
from app.features.users.infrastructure.models.user_model import Usuario

router = APIRouter(prefix="/appointments", tags=["Appointments"])

allow_doctor_or_receptionist = RoleChecker([RoleEnum.doctor, RoleEnum.recepcionist])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_appointment(
    data: AppointmentCreate, 
    usecase: CreateAppointmentUseCase = Depends(Provide[Container.create_appointment_use_case]),
    current_user: Usuario = Depends(allow_doctor_or_receptionist)
):
    try:
        entity = AppointmentEntity(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            appointment_date=data.appointment_date,
            reason=data.reason
        )
        return usecase.execute(entity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentResponse)
@inject
def get_appointment(
    appointment_id: int, 
    usecase: GetAppointmentUseCase = Depends(Provide[Container.get_appointment_use_case])
):
    try:
        return usecase.execute(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
@inject
def get_appointments_by_patient(
    patient_id: int, 
    usecase: GetAppointmentsByPatientUseCase = Depends(Provide[Container.get_appointments_by_patient_use_case])
):
    return usecase.execute(patient_id)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
@inject
def get_appointments_by_doctor(
    doctor_id: int, 
    usecase: GetAppointmentsByDoctorUseCase = Depends(Provide[Container.get_appointments_by_doctor_use_case])
):
    return usecase.execute(doctor_id)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
@inject
def update_appointment(
    appointment_id: int, 
    data: AppointmentUpdate, 
    usecase: UpdateAppointmentUseCase = Depends(Provide[Container.update_appointment_use_case]),
    current_user: Usuario = Depends(allow_doctor_or_receptionist)
):
    try:
        # In a cleaner architecture, the use case should take the ID and update dict directly
        # but for now we maintain existing functionality
        update_data = data.model_dump(exclude_unset=True)
        return usecase.execute(appointment_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_appointment(
    appointment_id: int, 
    usecase: DeleteAppointmentUseCase = Depends(Provide[Container.delete_appointment_use_case]),
    current_user: Usuario = Depends(allow_doctor_or_receptionist)
):
    try:
        usecase.execute(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
