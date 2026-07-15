from dependency_injector.wiring import inject, Provide
from container import Container
from fastapi import APIRouter, Depends, status
from typing import List

from app.users.infrastructure.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.users.infrastructure.controllers.user_controller import UserController

# El endpoint POST /login vive en el servicio auth (:8001), no aquí.
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_user(
    data: UserCreate,
    controller: UserController = Depends(Provide[Container.user_controller])
):
    return controller.create_user(data)

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
