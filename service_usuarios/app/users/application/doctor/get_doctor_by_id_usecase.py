from typing import Optional
from app.users.domain.ports import IDoctorRepository, IUserRepository


class GetDoctorByIdUseCase:
    def __init__(self, doctor_repository: IDoctorRepository, user_repository: IUserRepository):
        self.doctor_repository = doctor_repository
        self.user_repository = user_repository

    def execute(self, doctor_id: int) -> Optional[dict]:
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            return None

        user = self.user_repository.get_by_id(doctor.user_id)
        if not user:
            return None

        return {
            "doctor_id": doctor.doctor_id,
            "user_id": doctor.user_id,
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "image_url": user.image_url,
            "professional_license": doctor.professional_license,
            "specialty": doctor.specialty,
            "office": doctor.office,
        }
