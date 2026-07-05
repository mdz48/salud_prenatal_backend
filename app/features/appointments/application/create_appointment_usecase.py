from app.features.appointments.domain.ports import IAppointmentRepository, IPatientLookup, IDoctorLookup
from app.features.appointments.domain.appointment_entity import AppointmentEntity

class CreateAppointmentUseCase:
    def __init__(
        self,
        appointment_repo: IAppointmentRepository,
        patient_repo: IPatientLookup,
        doctor_repo: IDoctorLookup
    ):
        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo
        self.doctor_repo = doctor_repo

    def execute(self, entity: AppointmentEntity) -> AppointmentEntity:
        patient = self.patient_repo.get_by_id(entity.patient_id)
        if not patient:
            raise ValueError(f"Patient with id {entity.patient_id} not found")

        doctor = self.doctor_repo.get_by_id(entity.doctor_id)
        if not doctor:
            raise ValueError(f"Doctor with id {entity.doctor_id} not found")

        return self.appointment_repo.create(entity)
