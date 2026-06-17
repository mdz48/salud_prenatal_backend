from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.features.appointments.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.features.appointments.services.appointment_service import appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return appointment_service.create_appointment(db=db, data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        return appointment_service.get_appointment(db=db, appointment_id=appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
def get_appointments_by_patient(patient_id: int, db: Session = Depends(get_db)):
    return appointment_service.get_appointments_by_patient(db=db, patient_id=patient_id)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
def get_appointments_by_doctor(doctor_id: int, db: Session = Depends(get_db)):
    return appointment_service.get_appointments_by_doctor(db=db, doctor_id=doctor_id)

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):
    try:
        return appointment_service.update_appointment(db=db, appointment_id=appointment_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        appointment_service.delete_appointment(db=db, appointment_id=appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
