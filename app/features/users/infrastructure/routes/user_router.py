from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.features.users.infrastructure.schemas.user_schema import UserUpdate, UserResponse
from app.features.users.infrastructure.schemas.auth_schema import LoginRequest, Token
from app.features.users.application.user_usecases import GetUsersUseCase, GetUserUseCase, UpdateUserUseCase, DeleteUserUseCase
from app.features.users.application.auth_usecases import AuthenticateUserUseCase

router = APIRouter(prefix="/users", tags=["Users"])








@router.post("/login", response_model=Token)
@inject
def login(request: LoginRequest, usecase: AuthenticateUserUseCase = Depends(Provide[Container.authenticate_user_use_case])):
    try:
        return usecase.execute(request.email, request.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/", response_model=List[UserResponse])
@inject
def get_users(skip: int = 0, limit: int = 100, usecase: GetUsersUseCase = Depends(Provide[Container.get_users_use_case])):
    return usecase.execute(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
@inject
def get_user(user_id: int, usecase: GetUserUseCase = Depends(Provide[Container.get_user_use_case])):
    user = usecase.execute(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
@inject
def update_user(user_id: int, user: UserUpdate, usecase: UpdateUserUseCase = Depends(Provide[Container.update_user_use_case])):
    updated_user = usecase.execute(user_id=user_id, user=user)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_user(user_id: int, usecase: DeleteUserUseCase = Depends(Provide[Container.delete_user_use_case])):
    deleted = usecase.execute(user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
