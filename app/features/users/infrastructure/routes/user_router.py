from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status, Request, HTTPException
from typing import List

from app.features.users.infrastructure.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.features.users.infrastructure.schemas.auth_schema import LoginRequest, Token
from app.features.users.infrastructure.controllers.user_controller import UserController
from app.features.users.infrastructure.controllers.auth_controller import AuthController

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_user(
    data: UserCreate,
    controller: UserController = Depends(Provide[Container.user_controller])
):
    return controller.create_user(data)

@router.post("/login", response_model=Token)
@inject
async def login(
    request: Request,
    controller: AuthController = Depends(Provide[Container.auth_controller])
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Formato invalido. Envia JSON (email, password) o Form Data (username, password)."
            )

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requieren credenciales (email/username y password)."
        )

    return controller.login(email=str(email), password=str(password))

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
