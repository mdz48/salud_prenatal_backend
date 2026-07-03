from fastapi import HTTPException, status
from app.features.users.infrastructure.schemas.auth_schema import LoginRequest
from app.features.users.application.auth.authenticate_user_usecase import AuthenticateUserUseCase

class AuthController:
    def __init__(self, authenticate_user_use_case):
        self.authenticate_user_use_case = authenticate_user_use_case

    def login(self, request: LoginRequest):
        try:
            return self.authenticate_user_use_case.execute(request.email, request.password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
