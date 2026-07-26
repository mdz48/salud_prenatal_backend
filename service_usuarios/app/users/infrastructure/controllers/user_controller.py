from fastapi import HTTPException, status
from app.users.infrastructure.schemas.user_schema import UserCreate, UserUpdate
from app.users.domain.user_entity import UserEntity
from app.users.application.user.create_user_usecase import CreateUserUseCase
from app.users.application.user.get_users_usecase import GetUsersUseCase
from app.users.application.user.get_user_usecase import GetUserUseCase
from app.users.application.user.update_user_usecase import UpdateUserUseCase
from app.users.application.user.delete_user_usecase import DeleteUserUseCase

class UserController:
    def __init__(self, get_users_use_case, get_user_use_case, update_user_use_case, delete_user_use_case, create_user_use_case):
        self.get_users_use_case = get_users_use_case
        self.get_user_use_case = get_user_use_case
        self.update_user_use_case = update_user_use_case
        self.delete_user_use_case = delete_user_use_case
        self.create_user_use_case = create_user_use_case

    def create_user(self, data: UserCreate):
        try:
            entity = UserEntity(**data.model_dump())
            return self.create_user_use_case.execute(user=entity)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_users(self, skip: int, limit: int):
        return self.get_users_use_case.execute(skip=skip, limit=limit)

    def get_user(self, user_id: int):
        user = self.get_user_use_case.execute(user_id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update_user(self, user_id: int, user: UserUpdate):
        from app.users.application.dtos import UserUpdateDTO
        dto = UserUpdateDTO(**user.model_dump(exclude_unset=True))
        updated_user = self.update_user_use_case.execute(user_id=user_id, user=dto)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user

    def delete_user(self, user_id: int):
        deleted = self.delete_user_use_case.execute(user_id=user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return deleted
