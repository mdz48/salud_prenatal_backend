from typing import List, Optional
from app.features.users.domain.ports import IUserRepository
from app.features.users.domain.entities import UserEntity
from app.features.users.infrastructure.schemas.user_schema import UserUpdate
from app.core.security import get_password_hash

class GetUsersUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        return self.user_repository.get_all(skip=skip, limit=limit)

class GetUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int) -> Optional[UserEntity]:
        return self.user_repository.get_by_id(user_id)

class UpdateUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int, user: UserUpdate) -> Optional[UserEntity]:
        # Fetch the current user to get existing fields
        existing_user = self.user_repository.get_by_id(user_id)
        if not existing_user:
            return None
            
        update_data = user.model_dump(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['password'] = get_password_hash(update_data['password'])
            
        # create a new entity merging old data and new data
        merged_data = existing_user.model_dump()
        merged_data.update(update_data)
        updated_entity = UserEntity(**merged_data)
        
        return self.user_repository.update(user_id, updated_entity)

class DeleteUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int) -> Optional[UserEntity]:
        return self.user_repository.delete(user_id)
