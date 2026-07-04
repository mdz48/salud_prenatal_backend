from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.consultations.schemas.consultation_schema import ConsultationCreate, ConsultationResponse
from app.features.consultations.services.consultation_service import consultation_service

router = APIRouter(prefix="/consultations", tags=["Consultations"])

@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(data: ConsultationCreate, db: Session = Depends(get_db)):
    try:
        return consultation_service.create_consultation(db=db, data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/medical-record/{medical_record_id}", response_model=List[ConsultationResponse])
def get_consultations_by_medical_record(medical_record_id: int, db: Session = Depends(get_db)):
    return consultation_service.get_consultations_by_medical_record(db=db, medical_record_id=medical_record_id)

