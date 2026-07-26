from typing import Optional
from app.users.domain.ports import IUserRepository
from app.users.domain.user_entity import UserEntity

class DeleteUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int) -> Optional[UserEntity]:
        return self.user_repository.delete(user_id)
