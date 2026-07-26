from typing import Optional
from dataclasses import asdict
from app.users.domain.ports import IUserRepository
from app.users.domain.user_entity import UserEntity
from app.users.application.dtos import UserUpdateDTO
from salud_prenatal_shared_core.security import get_password_hash

class UpdateUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int, user: UserUpdateDTO) -> Optional[UserEntity]:
        # Fetch the current user to get existing fields
        existing_user = self.user_repository.get_by_id(user_id)
        if not existing_user:
            return None
            
        update_data = {k: v for k, v in asdict(user).items() if v is not None}
        if 'password' in update_data and update_data['password']:
            update_data['password'] = get_password_hash(update_data['password'])
            
        # create a new entity merging old data and new data
        merged_data = existing_user.model_dump()
        merged_data.update(update_data)
        updated_entity = UserEntity(**merged_data)
        
        return self.user_repository.update(user_id, updated_entity)
