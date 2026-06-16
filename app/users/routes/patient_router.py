from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.users.schemas.patient_schema import PatientRegistration, PatientResponse
from app.users.services.patient_service import patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(data: PatientRegistration, db: Session = Depends(get_db)):
    try:
        return patient_service.register_patient(db=db, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the patient.")
