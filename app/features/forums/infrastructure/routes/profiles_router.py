from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.core.dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from app.features.forums.infrastructure.schemas.forums_schemas import ProfileCreate, ProfileResponse
from app.features.forums.infrastructure.controllers.profiles_controller import ProfilesController
from app.features.users.domain.user_entity import UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Profiles"])

@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_profile(
    data: ProfileCreate,
    current_user: UserEntity = Depends(get_current_user),
    controller: ProfilesController = Depends(Provide[Container.profiles_controller])
):
    return controller.create_profile(data, current_user.user_id)

@router.get("/profiles/{user_id}", response_model=ProfileResponse)
@inject
def get_profile(
    user_id: int,
    controller: ProfilesController = Depends(Provide[Container.profiles_controller])
):
    return controller.get_profile(user_id)
