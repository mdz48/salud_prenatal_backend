"""Implementa IAppointmentLookup leyendo la tabla `appointments` directamente de
la DB compartida (read-model), en vez de llamar al repositorio del servicio
transaccional. El puerto no cambia; solo cambia esta implementación.
"""
from typing import List
from sqlalchemy.orm import Session
from app.users.domain.ports import IAppointmentLookup
from app.users.infrastructure.readmodels.appointment_readmodel import AppointmentRead


class AppointmentLookupAdapter(IAppointmentLookup):
    def __init__(self, db: Session):
        self.db = db

    def get_appointments_by_patient_id(self, patient_id: int) -> List[object]:
        return self.db.query(AppointmentRead).filter(AppointmentRead.patient_id == patient_id).all()

    def get_appointments_by_doctor_id(self, doctor_id: int) -> List[object]:
        return self.db.query(AppointmentRead).filter(AppointmentRead.doctor_id == doctor_id).all()

    def cancel_future_appointments(self, patient_id: int, doctor_id: int) -> None:
        from app.users.infrastructure.readmodels.appointment_readmodel import AppointmentRead
        from salud_prenatal_shared_core.enums import AppointmentStatusEnum
        from salud_prenatal_shared_core.time import now_cdmx
        
        now = now_cdmx().replace(tzinfo=None)
        self.db.query(AppointmentRead).filter(
            AppointmentRead.patient_id == patient_id,
            AppointmentRead.doctor_id == doctor_id,
            AppointmentRead.appointment_date >= now,
            AppointmentRead.status.in_([AppointmentStatusEnum.pending, AppointmentStatusEnum.confirmed])
        ).update({AppointmentRead.status: AppointmentStatusEnum.cancelled}, synchronize_session=False)
        self.db.commit()
