from sqlalchemy.orm import Session
from app.features.users.schemas.patient_schema import PatientRegistration
from app.core.security import get_password_hash
from app.core.enums import RoleEnum
from app.features.users.repositories.user_repository import user_repository
from app.features.users.repositories.patient_repository import patient_repository

class PatientService:
    def register_patient(self, db: Session, data: PatientRegistration):
        existing_user = user_repository.get_by_email(db, data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user_data = {
            "name": data.name,
            "last_name": data.last_name,
            "email": data.email,
            "phone": data.phone,
            "role": RoleEnum.patient,
            "is_active": True,
            "password": get_password_hash(data.password)
        }
        
        try:
            db_user = user_repository.create_from_dict(db, user_data, commit=False)
            
            patient_data_dict = data.model_dump(exclude={"name", "last_name", "email", "phone", "password", "role", "is_active", "image_url"})
            patient_data_dict["user_id"] = db_user.user_id
            
            db_patient = patient_repository.create(db, patient_data_dict, commit=False)
            
            db.commit()
            db.refresh(db_user)
            db.refresh(db_patient)
            
            return db_patient
        except Exception as e:
            db.rollback()
            raise e

    def get_patients_by_doctor(self, db: Session, doctor_id: int):
        return patient_repository.get_by_doctor_id(db, doctor_id)

    def get_patient_dashboard(self, db: Session, patient_id: int):
        from datetime import datetime
        patient = patient_repository.get_by_id(db, patient_id)
        if not patient:
            raise ValueError("Patient not found")

        full_name = f"{patient.user.name} {patient.user.last_name}"
        gestational_weeks = patient.current_gestational_weeks

        current_doctor = None
        current_doctor_image = None
        current_doctor_specialty = None
        
        if patient.doctor and patient.doctor.user:
            current_doctor = f"{patient.doctor.user.name} {patient.doctor.user.last_name}"
            current_doctor_image = patient.doctor.user.image_url
            current_doctor_specialty = patient.doctor.specialty

        now = datetime.utcnow()
        upcoming_appointments = []
        for appt in patient.appointments:
            # We assume timezone-naive datetime or matching timezone
            if appt.appointment_date >= now:
                upcoming_appointments.append({
                    "appointment_id": appt.appointment_id,
                    "appointment_date": appt.appointment_date,
                    "status": appt.status.value if hasattr(appt.status, 'value') else str(appt.status),
                    "reason": appt.reason,
                    "doctor_name": f"{appt.doctor.user.name} {appt.doctor.user.last_name}" if appt.doctor and appt.doctor.user else "Unknown"
                })

        upcoming_appointments.sort(key=lambda x: x["appointment_date"])

        return {
            "full_name": full_name,
            "current_gestational_weeks": gestational_weeks,
            "current_doctor": current_doctor,
            "current_doctor_image": current_doctor_image,
            "current_doctor_specialty": current_doctor_specialty,
            "upcoming_appointments": upcoming_appointments
        }

patient_service = PatientService()
