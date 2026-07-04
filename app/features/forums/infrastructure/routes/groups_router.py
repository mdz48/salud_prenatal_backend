from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from typing import List
from app.features.forums.infrastructure.schemas.forums_schemas import GroupCreate, GroupResponse
from app.features.forums.infrastructure.controllers.groups_controller import GroupsController

router = APIRouter(prefix="/forums", tags=["Forums - Groups"])

@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_group(
    data: GroupCreate,
    controller: GroupsController = Depends(Provide[Container.groups_controller])
):
    return controller.create_group(data)

@router.get("/groups", response_model=List[GroupResponse])
@inject
def get_groups(
    controller: GroupsController = Depends(Provide[Container.groups_controller])
):
    return controller.get_groups()
