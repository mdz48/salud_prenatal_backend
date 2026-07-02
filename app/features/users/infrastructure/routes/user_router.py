from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from typing import List

from app.features.users.infrastructure.schemas.user_schema import UserUpdate, UserResponse
from app.features.users.infrastructure.schemas.auth_schema import LoginRequest, Token
from app.features.users.infrastructure.controllers.user_controller import UserController
from app.features.users.infrastructure.controllers.auth_controller import AuthController

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/login", response_model=Token)
@inject
def login(request: LoginRequest, controller: AuthController = Depends(Provide[Container.auth_controller])):
    return controller.login(request)

@router.get("/", response_model=List[UserResponse])
@inject
def get_users(skip: int = 0, limit: int = 100, controller: UserController = Depends(Provide[Container.user_controller])):
    return controller.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
@inject
def get_user(user_id: int, controller: UserController = Depends(Provide[Container.user_controller])):
    return controller.get_user(user_id=user_id)

@router.put("/{user_id}", response_model=UserResponse)
@inject
def update_user(user_id: int, user: UserUpdate, controller: UserController = Depends(Provide[Container.user_controller])):
    return controller.update_user(user_id=user_id, user=user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_user(user_id: int, controller: UserController = Depends(Provide[Container.user_controller])):
    return controller.delete_user(user_id=user_id)
