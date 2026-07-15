from typing import Optional
from app.users.domain.ports import IReceptionistRepository, IUserRepository


class GetReceptionistByIdUseCase:
    def __init__(self, receptionist_repository: IReceptionistRepository, user_repository: IUserRepository):
        self.receptionist_repository = receptionist_repository
        self.user_repository = user_repository

    def execute(self, receptionist_id: int) -> Optional[dict]:
        receptionist = self.receptionist_repository.get_by_id(receptionist_id)
        if not receptionist:
            return None

        user = self.user_repository.get_by_id(receptionist.user_id)
        if not user:
            return None

        return {
            "receptionist_id": receptionist.receptionist_id,
            "user_id": receptionist.user_id,
            "doctor_id": receptionist.doctor_id,
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "image_url": user.image_url,
        }
