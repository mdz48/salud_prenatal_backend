from typing import Optional
from app.appointments.domain.ports import IAppointmentRepository, IPatientLookup, IDoctorLookup
from app.appointments.domain.appointment_entity import AppointmentEntity
from app.core.events.domain_event import AppointmentCreatedEvent
from app.core.events.event_dispatcher import IEventDispatcher


class CreateAppointmentUseCase:
    def __init__(
        self,
        appointment_repo: IAppointmentRepository,
        patient_repo: IPatientLookup,
        doctor_repo: IDoctorLookup,
        event_dispatcher: Optional[IEventDispatcher] = None,
    ):
        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo
        self.doctor_repo = doctor_repo
        self.event_dispatcher = event_dispatcher

    def execute(self, entity: AppointmentEntity) -> AppointmentEntity:
        patient = self.patient_repo.get_by_id(entity.patient_id)
        if not patient:
            raise ValueError(f"Patient with id {entity.patient_id} not found")

        doctor = self.doctor_repo.get_by_id(entity.doctor_id)
        if not doctor:
            raise ValueError(f"Doctor with id {entity.doctor_id} not found")

        created = self.appointment_repo.create(entity)

        if self.event_dispatcher and created.appointment_id:
            self.event_dispatcher.publish(
                AppointmentCreatedEvent(
                    appointment_id=created.appointment_id,
                    patient_id=created.patient_id,
                    doctor_id=created.doctor_id,
                    appointment_date=created.appointment_date,
                    reason=created.reason,
                )
            )

        return created
