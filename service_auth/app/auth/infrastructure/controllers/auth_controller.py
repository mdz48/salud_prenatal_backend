from fastapi import HTTPException, status

from app.auth.application.authenticate_user_usecase import AuthenticateUserUseCase


class AuthController:
    def __init__(self, authenticate_user_use_case: AuthenticateUserUseCase):
        self.authenticate_user_use_case = authenticate_user_use_case

    def login(self, email: str, password: str):
        try:
            return self.authenticate_user_use_case.execute(email, password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
