from app.features.users.domain.ports import IPatientRepository

class GetPatientsByDoctorUseCase:
    def __init__(self, patient_repository: IPatientRepository):
        self.patient_repository = patient_repository

    def execute(self, doctor_id: int):
        return self.patient_repository.get_patients_by_doctor(doctor_id)
