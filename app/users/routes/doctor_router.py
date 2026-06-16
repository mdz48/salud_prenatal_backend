from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.users.schemas.doctor_schema import DoctorRegistration, DoctorResponse
from app.users.services.doctor_service import doctor_service

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def register_doctor(data: DoctorRegistration, db: Session = Depends(get_db)):
    try:
        return doctor_service.register_doctor(db=db, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the doctor.")
