from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from app.features.users.infrastructure.schemas.doctor_schema import DoctorRegistration, DoctorResponse
from app.features.users.infrastructure.schemas.patient_schema import PatientResponse
from app.features.users.infrastructure.schemas.invitation_code_schema import InvitationCodeResponse
from app.features.users.infrastructure.schemas.receptionist_schema import ReceptionistCreate, ReceptionistResponse
from typing import List


from app.features.users.application.doctor_usecases import CreateReceptionistUseCase, GetReceptionistsByDoctorUseCase, RegisterDoctorUseCase, GenerateInvitationCodeUseCase
from app.features.users.application.patient_usecases import GetPatientsByDoctorUseCase

router = APIRouter(prefix="/doctors", tags=["Doctors"])







@router.post("/{doctor_id}/receptionists", response_model=ReceptionistResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_receptionist(doctor_id: int, data: ReceptionistCreate, usecase: CreateReceptionistUseCase = Depends(Provide[Container.create_receptionist_use_case])):
    try:
        return usecase.execute(doctor_id=doctor_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error creating receptionist: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the receptionist.")

@router.get("/{doctor_id}/receptionists", response_model=List[ReceptionistResponse], status_code=status.HTTP_200_OK)
@inject
def get_receptionists_by_doctor(doctor_id: int, usecase: GetReceptionistsByDoctorUseCase = Depends(Provide[Container.get_receptionists_by_doctor_use_case])):
    try:
        return usecase.execute(doctor_id=doctor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print(f"Error fetching receptionists: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching receptionists.")

@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
@inject
def register_doctor(data: DoctorRegistration, usecase: RegisterDoctorUseCase = Depends(Provide[Container.register_doctor_use_case])):
    try:
        return usecase.execute(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error registering doctor: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the doctor.")

@router.get("/{doctor_id}/patients", response_model=List[PatientResponse], status_code=status.HTTP_200_OK)
@inject
def get_patients_by_doctor(doctor_id: int, usecase: GetPatientsByDoctorUseCase = Depends(Provide[Container.get_patients_by_doctor_use_case])):
    try:
        return usecase.execute(doctor_id=doctor_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching patients.")

@router.post("/{doctor_id}/invitation-code", response_model=InvitationCodeResponse, status_code=status.HTTP_201_CREATED)
@inject
def generate_invitation_code(doctor_id: int, usecase: GenerateInvitationCodeUseCase = Depends(Provide[Container.generate_invitation_code_use_case])):
    try:
        return usecase.execute(doctor_id=doctor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while generating the invitation code.")
