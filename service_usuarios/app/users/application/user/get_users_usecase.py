from typing import List
from app.users.domain.ports import IUserRepository
from app.users.domain.user_entity import UserEntity

class GetUsersUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        return self.user_repository.get_all(skip=skip, limit=limit)
