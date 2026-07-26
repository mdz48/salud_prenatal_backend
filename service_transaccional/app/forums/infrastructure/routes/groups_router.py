from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from salud_prenatal_shared_core.auth_dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from typing import List
from app.forums.infrastructure.schemas.forums_schemas import GroupCreate, GroupResponse
from app.forums.infrastructure.controllers.groups_controller import GroupsController
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Groups"])


@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_group(
    data: GroupCreate,
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.groups_controller()
    return controller.create_group(data, current_user.user_id)


@router.get("/groups/recommended", response_model=List[GroupResponse])
@close_db_after(Container)
def get_recommended_groups(
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.groups_controller()
    return controller.get_recommended_groups(current_user.user_id)


@router.get("/groups", response_model=List[GroupResponse])
@close_db_after(Container)
def get_groups():
    controller = Container.groups_controller()
    return controller.get_groups()
