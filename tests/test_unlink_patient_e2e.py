from datetime import datetime, timedelta
import pytest
from app.core.database import get_session_factory
from app.features.users.infrastructure.models.user_model import Usuario
from app.features.users.infrastructure.models.doctor_model import Doctor
from app.features.users.infrastructure.models.patient_model import Patient
from app.features.appointments.infrastructure.models.appointment_model import Appointment
from app.core.enums import AppointmentStatusEnum, RoleEnum

@pytest.mark.integration
def test_unlink_patient_e2e(client):
    db = get_session_factory()()
    try:
        # Create doctor
        doc_user = Usuario(
            name="Elena",
            last_name="Rios",
            email="doc.unlink.e2e@test.com",
            password="secret123",
            role=RoleEnum.doctor,
            is_active=True
        )
        db.add(doc_user)
        db.commit()

        doctor = Doctor(user_id=doc_user.user_id, professional_license="LIC-E2E-1", specialty="Obstetricia")
        db.add(doctor)
        db.commit()

        # Create patient linked to doctor
        pat_user = Usuario(
            name="Maria",
            last_name="Lopez",
            email="pat.unlink.e2e@test.com",
            password="secret123",
            role=RoleEnum.patient,
            is_active=True
        )
        db.add(pat_user)
        db.commit()

        patient = Patient(user_id=pat_user.user_id, doctor_id=doctor.doctor_id, birthdate=datetime(1995, 4, 10).date())
        db.add(patient)
        db.commit()

        # Create a future pending appointment between them
        future_date = datetime.utcnow() + timedelta(days=5)
        appointment = Appointment(
            patient_id=patient.patient_id,
            doctor_id=doctor.doctor_id,
            appointment_date=future_date,
            status=AppointmentStatusEnum.pending,
            reason="Checkup E2E"
        )
        db.add(appointment)
        db.commit()

        # Check they are linked before deleting
        assert patient.doctor_id == doctor.doctor_id

        # Call the endpoint to unlink
        response = client.delete(f"/api/v1/doctors/{doctor.doctor_id}/patients/{patient.patient_id}")
        assert response.status_code == 200, response.text
        
        # Verify response
        data = response.json()
        assert data["patient_id"] == patient.patient_id
        assert data["doctor_id"] is None

        # Verify database state
        db.refresh(patient)
        db.refresh(appointment)

        assert patient.doctor_id is None
        assert appointment.status == AppointmentStatusEnum.cancelled

    finally:
        db.close()
