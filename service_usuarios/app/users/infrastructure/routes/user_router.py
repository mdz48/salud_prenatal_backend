from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from fastapi import APIRouter, Depends, status
from typing import List

from app.users.infrastructure.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.users.infrastructure.controllers.user_controller import UserController

# El endpoint POST /login vive en el servicio auth (:8001), no aquí.
router = APIRouter(prefix="/users", tags=["Users"])


# Deshabilitado: ruta sin ningún control de auth/rol (creaba y listaba usuarios
# arbitrarios sin token). Solo se usaba para seed/dev, ya no debe estar expuesta.
# @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# @close_db_after(Container)
# def create_user(
#     data: UserCreate,
# ):
#     controller = Container.user_controller()
#     return controller.create_user(data)
#
#
# @router.get("/", response_model=List[UserResponse])
# @close_db_after(Container)
# def get_users(skip: int = 0, limit: int = 100):
#     controller = Container.user_controller()
#     return controller.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
@close_db_after(Container)
def get_user(user_id: int):
    controller = Container.user_controller()
    return controller.get_user(user_id=user_id)


@router.put("/{user_id}", response_model=UserResponse)
@close_db_after(Container)
def update_user(user_id: int, user: UserUpdate):
    controller = Container.user_controller()
    return controller.update_user(user_id=user_id, user=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@close_db_after(Container)
def delete_user(user_id: int):
    controller = Container.user_controller()
    return controller.delete_user(user_id=user_id)
