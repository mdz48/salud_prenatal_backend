from fastapi import HTTPException, status
from app.features.users.infrastructure.schemas.user_schema import UserUpdate

class UserController:
    def __init__(self, get_users_use_case, get_user_use_case, update_user_use_case, delete_user_use_case):
        self.get_users_use_case = get_users_use_case
        self.get_user_use_case = get_user_use_case
        self.update_user_use_case = update_user_use_case
        self.delete_user_use_case = delete_user_use_case

    def get_users(self, skip: int, limit: int):
        return self.get_users_use_case.execute(skip=skip, limit=limit)

    def get_user(self, user_id: int):
        user = self.get_user_use_case.execute(user_id=user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update_user(self, user_id: int, user: UserUpdate):
        updated_user = self.update_user_use_case.execute(user_id=user_id, user=user)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user

    def delete_user(self, user_id: int):
        deleted = self.delete_user_use_case.execute(user_id=user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return deleted
