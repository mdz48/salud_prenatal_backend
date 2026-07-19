from app.users.domain.ports import IDoctorRepository, IReceptionistRepository

class GetReceptionistsByDoctorUseCase:
    def __init__(self, doctor_repository: IDoctorRepository, receptionist_repository: IReceptionistRepository):
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository

    def execute(self, doctor_id: int):
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        return self.receptionist_repository.get_by_doctor_id(doctor_id)
