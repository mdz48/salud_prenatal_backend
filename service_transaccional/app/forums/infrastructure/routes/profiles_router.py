from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from salud_prenatal_shared_core.auth_dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from app.forums.infrastructure.schemas.forums_schemas import (
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfileTimelineResponse
)
from app.forums.infrastructure.controllers.profiles_controller import ProfilesController
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Profiles"])


@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_profile(
    data: ProfileCreate,
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.profiles_controller()
    return controller.create_profile(data, current_user.user_id)


@router.patch("/profiles/me", response_model=ProfileResponse)
@close_db_after(Container)
def update_my_profile(
    data: ProfileUpdate,
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.profiles_controller()
    return controller.update_profile(data, current_user.user_id)


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
@close_db_after(Container)
def get_profile(
    user_id: int,
):
    controller = Container.profiles_controller()
    return controller.get_profile(user_id)


@router.get("/profiles/{user_id}/timeline", response_model=ProfileTimelineResponse)
@close_db_after(Container)
def get_profile_timeline(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
):
    controller = Container.profiles_controller()
    return controller.get_profile_timeline(user_id, limit, offset)
