from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.core.dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from typing import List
from app.features.forums.infrastructure.schemas.forums_schemas import GroupCreate, GroupResponse
from app.features.forums.infrastructure.controllers.groups_controller import GroupsController
from app.features.users.domain.user_entity import UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Groups"])

@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_group(
    data: GroupCreate,
    current_user: UserEntity = Depends(get_current_user),
    controller: GroupsController = Depends(Provide[Container.groups_controller])
):
    return controller.create_group(data, current_user.user_id)

@router.get("/groups/recommended", response_model=List[GroupResponse])
@inject
def get_recommended_groups(
    current_user: UserEntity = Depends(get_current_user),
    controller: GroupsController = Depends(Provide[Container.groups_controller])
):
    return controller.get_recommended_groups(current_user.user_id)

@router.get("/groups", response_model=List[GroupResponse])
@inject
def get_groups(
    controller: GroupsController = Depends(Provide[Container.groups_controller])
):
    return controller.get_groups()
