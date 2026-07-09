from typing import Optional

from app.core.events.event_bus import EventBus
from app.core.events.events import AppointmentCreatedEvent
from app.features.appointments.application.specifications import (
    DoctorExistsSpecification,
    PatientExistsSpecification,
)
from app.features.appointments.domain.ports import IAppointmentRepository, IPatientLookup, IDoctorLookup
from app.features.appointments.domain.appointment_entity import AppointmentEntity

class CreateAppointmentUseCase:
    def __init__(
        self,
        appointment_repo: IAppointmentRepository,
        patient_repo: IPatientLookup,
        doctor_repo: IDoctorLookup,
        event_bus: Optional[EventBus] = None,
    ):
        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo
        self.doctor_repo = doctor_repo
        self.event_bus = event_bus

    def execute(self, entity: AppointmentEntity) -> AppointmentEntity:
        if not PatientExistsSpecification(self.patient_repo).is_satisfied_by(entity):
            raise ValueError(f"Patient with id {entity.patient_id} not found")

        if not DoctorExistsSpecification(self.doctor_repo).is_satisfied_by(entity):
            raise ValueError(f"Doctor with id {entity.doctor_id} not found")

        created = self.appointment_repo.create(entity)

        if self.event_bus:
            self.event_bus.publish(
                AppointmentCreatedEvent(
                    appointment_id=created.appointment_id,
                    patient_id=created.patient_id,
                    doctor_id=created.doctor_id,
                )
            )

        return created
