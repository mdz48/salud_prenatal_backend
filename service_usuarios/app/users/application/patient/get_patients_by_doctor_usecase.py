from app.users.domain.ports import IPatientRepository, IMedicalRecordLookup

class GetPatientsByDoctorUseCase:
    def __init__(self, patient_repository: IPatientRepository, medical_record_lookup: IMedicalRecordLookup):
        self.patient_repository = patient_repository
        self.medical_record_lookup = medical_record_lookup

    def execute(self, doctor_id: int):
        patients = self.patient_repository.get_patients_by_doctor(doctor_id)
        result = []
        for patient in patients:
            full_name = f"{patient.user.name} {patient.user.last_name}" if patient.user else None
            gestational_weeks = self.medical_record_lookup.get_current_gestational_weeks(patient.patient_id, doctor_id)
            result.append({
                "patient_id": patient.patient_id,
                "user_id": patient.user_id,
                "doctor_id": patient.doctor_id,
                "birthdate": patient.birthdate,
                "full_name": full_name,
                "current_gestational_weeks": gestational_weeks,
                "age": patient.age,
            })
        return result
