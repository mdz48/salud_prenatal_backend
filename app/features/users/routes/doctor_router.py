from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.users.schemas.doctor_schema import DoctorRegistration, DoctorResponse
from app.features.users.schemas.patient_schema import PatientResponse
from app.features.users.schemas.invitation_code_schema import InvitationCodeResponse
from app.features.users.services.doctor_service import doctor_service
from app.features.users.services.patient_service import patient_service
from typing import List

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def register_doctor(data: DoctorRegistration, db: Session = Depends(get_db)):
    try:
        return doctor_service.register_doctor(db=db, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error registering doctor: {repr(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the doctor.")

@router.get("/{doctor_id}/patients", response_model=List[PatientResponse], status_code=status.HTTP_200_OK)
def get_patients_by_doctor(doctor_id: int, db: Session = Depends(get_db)):
    try:
        return patient_service.get_patients_by_doctor(db=db, doctor_id=doctor_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching patients.")

@router.post("/{doctor_id}/invitation-code", response_model=InvitationCodeResponse, status_code=status.HTTP_201_CREATED)
def generate_invitation_code(doctor_id: int, db: Session = Depends(get_db)):
    try:
        return doctor_service.generate_invitation_code(db=db, doctor_id=doctor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while generating the invitation code.")
