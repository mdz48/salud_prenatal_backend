from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.users.schemas.patient_schema import PatientRegistration, PatientResponse
from app.features.users.schemas.invitation_code_schema import RedeemCodeRequest
from app.features.users.services.patient_service import patient_service
from app.features.users.services.invitation_service import invitation_service

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(data: PatientRegistration, db: Session = Depends(get_db)):
    try:
        return patient_service.register_patient(db=db, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while registering the patient.")

@router.post("/{patient_id}/redeem-code", response_model=PatientResponse, status_code=status.HTTP_200_OK)
def redeem_code(patient_id: int, data: RedeemCodeRequest, db: Session = Depends(get_db)):
    try:
        return invitation_service.redeem_code(db=db, code=data.code, patient_id=patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while redeeming the code.")
