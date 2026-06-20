from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.patient_diaries.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate, PatientDiaryResponse
from app.features.patient_diaries.services.patient_diary_service import patient_diary_service

router = APIRouter(prefix="/patient-diaries", tags=["Patient Diaries"])

@router.post("/", response_model=PatientDiaryResponse, status_code=status.HTTP_201_CREATED)
def create_patient_diary(data: PatientDiaryCreate, db: Session = Depends(get_db)):
    try:
        return patient_diary_service.create(db=db, data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[PatientDiaryResponse])
def get_all_patient_diaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return patient_diary_service.get_all(db=db, skip=skip, limit=limit)

@router.get("/medical-record/{medical_record_id}", response_model=List[PatientDiaryResponse])
def get_diaries_by_medical_record(medical_record_id: int, db: Session = Depends(get_db)):
    return patient_diary_service.get_by_medical_record_id(db=db, medical_record_id=medical_record_id)

@router.get("/{patient_diary_id}", response_model=PatientDiaryResponse)
def get_patient_diary(patient_diary_id: int, db: Session = Depends(get_db)):
    try:
        return patient_diary_service.get_by_id(db=db, patient_diary_id=patient_diary_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{patient_diary_id}", response_model=PatientDiaryResponse)
def update_patient_diary(patient_diary_id: int, data: PatientDiaryUpdate, db: Session = Depends(get_db)):
    try:
        return patient_diary_service.update(db=db, patient_diary_id=patient_diary_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{patient_diary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_diary(patient_diary_id: int, db: Session = Depends(get_db)):
    try:
        patient_diary_service.delete(db=db, patient_diary_id=patient_diary_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
