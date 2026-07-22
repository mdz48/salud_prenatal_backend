from typing import Protocol

from app.appointments.domain.appointment_entity import AppointmentEntity
from app.appointments.domain.ports import IAppointmentRepository, IPatientLookup
from salud_prenatal_shared_core.enums import AppointmentStatusEnum


class IAppointmentSpecification(Protocol):
    def is_satisfied_by(self, entity: AppointmentEntity) -> bool: ...
    def error_message(self) -> str: ...


class DoctorAvailabilitySpecification:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def is_satisfied_by(self, entity: AppointmentEntity) -> bool:
        existing_appointments = self.appointment_repo.get_by_doctor_id(entity.doctor_id)
        for appt in existing_appointments:
            if appt.appointment_date == entity.appointment_date and appt.status != AppointmentStatusEnum.cancelled:
                return False
        return True

    def error_message(self) -> str:
        return "El doctor ya tiene una cita agendada en la fecha y hora seleccionadas."


class ActivePatientLinkSpecification:
    def __init__(self, patient_lookup: IPatientLookup):
        self.patient_lookup = patient_lookup

    def is_satisfied_by(self, entity: AppointmentEntity) -> bool:
        patient = self.patient_lookup.get_by_id(entity.patient_id)
        return patient is not None and getattr(patient, "doctor_id", None) == entity.doctor_id

    def error_message(self) -> str:
        return "El paciente no tiene una vinculación activa con el médico tratante."
