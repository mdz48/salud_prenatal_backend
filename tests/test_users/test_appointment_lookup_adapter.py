from datetime import datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # registers all models in Base
from app.core.database import Base
from app.core.enums import AppointmentStatusEnum
from app.features.appointments.infrastructure.models.appointment_model import Appointment
from app.features.appointments.infrastructure.repositories.appointment_repository import AppointmentRepository
from app.features.users.infrastructure.adapters.appointment_lookup_adapter import AppointmentLookupAdapter

@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()

def test_cancel_future_appointments(db_session):
    # Setup appointments
    now = datetime.utcnow()
    future_date = now + timedelta(days=2)
    past_date = now - timedelta(days=2)

    # 1. Future pending appointment between patient 1 and doctor 2
    app1 = Appointment(
        patient_id=1,
        doctor_id=2,
        appointment_date=future_date,
        status=AppointmentStatusEnum.pending,
        reason="Checkup 1"
    )

    # 2. Future confirmed appointment between patient 1 and doctor 2
    app2 = Appointment(
        patient_id=1,
        doctor_id=2,
        appointment_date=future_date,
        status=AppointmentStatusEnum.confirmed,
        reason="Checkup 2"
    )

    # 3. Past pending appointment between patient 1 and doctor 2 (should not be cancelled)
    app3 = Appointment(
        patient_id=1,
        doctor_id=2,
        appointment_date=past_date,
        status=AppointmentStatusEnum.pending,
        reason="Checkup 3"
    )

    # 4. Future pending appointment for a different patient (should not be cancelled)
    app4 = Appointment(
        patient_id=9,
        doctor_id=2,
        appointment_date=future_date,
        status=AppointmentStatusEnum.pending,
        reason="Checkup 4"
    )

    db_session.add_all([app1, app2, app3, app4])
    db_session.commit()

    repo = AppointmentRepository(db_session)
    adapter = AppointmentLookupAdapter(repo)

    # Call cancellation
    adapter.cancel_future_appointments(patient_id=1, doctor_id=2)

    # Refresh and assert
    db_session.refresh(app1)
    db_session.refresh(app2)
    db_session.refresh(app3)
    db_session.refresh(app4)

    assert app1.status == AppointmentStatusEnum.cancelled
    assert app2.status == AppointmentStatusEnum.cancelled
    assert app3.status == AppointmentStatusEnum.pending
    assert app4.status == AppointmentStatusEnum.pending
