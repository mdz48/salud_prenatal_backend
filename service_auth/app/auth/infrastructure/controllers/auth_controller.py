from fastapi import HTTPException, status

from app.auth.application.authenticate_user_usecase import AuthenticateUserUseCase
from app.auth.application.refresh_token_usecase import RefreshTokenUseCase


class AuthController:
    def __init__(
        self,
        authenticate_user_use_case: AuthenticateUserUseCase,
        refresh_token_use_case: RefreshTokenUseCase,
    ):
        self.authenticate_user_use_case = authenticate_user_use_case
        self.refresh_token_use_case = refresh_token_use_case

    def login(self, email: str, password: str):
        try:
            return self.authenticate_user_use_case.execute(email, password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    def refresh(self, email: str, user_id: int, role: str):
        return self.refresh_token_use_case.execute(email=email, user_id=user_id, role=role)
