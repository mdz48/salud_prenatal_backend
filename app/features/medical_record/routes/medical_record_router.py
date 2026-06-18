from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.medical_record.schemas.medical_record_schema import PatientMedicalRecordResponse
from app.features.medical_record.services.medical_record_service import medical_record_service

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])

@router.get("/patient/{patient_id}", response_model=PatientMedicalRecordResponse, status_code=status.HTTP_200_OK)
def get_patient_medical_record(patient_id: int, db: Session = Depends(get_db)):
    try:
        return medical_record_service.get_patient_medical_record(db=db, patient_id=patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the medical record.")
