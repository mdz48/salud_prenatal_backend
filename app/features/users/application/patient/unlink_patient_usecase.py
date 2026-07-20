from app.features.users.domain.ports import IPatientRepository, IAppointmentLookup
from app.features.users.domain.patient_entity import PatientEntity

class UnlinkPatientUseCase:
    def __init__(self, patient_repository: IPatientRepository, appointment_lookup: IAppointmentLookup):
        self.patient_repository = patient_repository
        self.appointment_lookup = appointment_lookup

    def execute(self, doctor_id: int, patient_id: int) -> PatientEntity:
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        if patient.doctor_id != doctor_id:
            raise ValueError("Patient does not belong to this doctor")

        self.appointment_lookup.cancel_future_appointments(patient_id, doctor_id)
        
        updated_patient = self.patient_repository.update_doctor(patient_id, None)
        if not updated_patient:
            raise ValueError("Failed to update patient association")
            
        return updated_patient
