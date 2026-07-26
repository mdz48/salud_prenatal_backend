from app.users.domain.ports import IUserRepository
from app.users.domain.user_entity import UserEntity
from salud_prenatal_shared_core.security import get_password_hash

class CreateUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user: UserEntity) -> UserEntity:
        existing_user = self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = get_password_hash(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password

        user_to_create = UserEntity(**user_data)
        return self.user_repository.create(user_to_create)
