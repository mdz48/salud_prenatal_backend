from app.features.users.domain.ports import IDoctorRepository, IInvitationCodeRepository

class GenerateInvitationCodeUseCase:
    def __init__(self, doctor_repository: IDoctorRepository, invitation_code_repository: IInvitationCodeRepository):
        self.doctor_repository = doctor_repository
        self.invitation_code_repository = invitation_code_repository

    def execute(self, doctor_id: int):
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        return self.invitation_code_repository.create(doctor_id)
