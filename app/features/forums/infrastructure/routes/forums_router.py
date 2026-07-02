from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from typing import List
from app.features.forums.domain.entities import (
    SocialProfileEntity,
    CommunityGroupEntity,
    PostEntity,
    CommentEntity,
    ReportEntity
)
from app.features.forums.infrastructure.controllers.forums_controller import ForumsController

router = APIRouter(prefix="/forums", tags=["Forums"])

@router.post("/profiles", response_model=SocialProfileEntity, status_code=status.HTTP_201_CREATED)
@inject
def create_profile(
    data: SocialProfileEntity,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.create_profile(data)

@router.get("/profiles/{user_id}", response_model=SocialProfileEntity)
@inject
def get_profile(
    user_id: int,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.get_profile(user_id)

@router.post("/groups", response_model=CommunityGroupEntity, status_code=status.HTTP_201_CREATED)
@inject
def create_group(
    data: CommunityGroupEntity,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.create_group(data)

@router.get("/groups", response_model=List[CommunityGroupEntity])
@inject
def get_groups(
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.get_groups()

@router.post("/posts", response_model=PostEntity, status_code=status.HTTP_201_CREATED)
@inject
def create_post(
    data: PostEntity,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.create_post(data)

@router.get("/posts/global", response_model=List[PostEntity])
@inject
def get_global_feed(
    limit: int = 50,
    offset: int = 0,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.get_global_feed(limit, offset)

@router.get("/groups/{group_id}/posts", response_model=List[PostEntity])
@inject
def get_group_feed(
    group_id: int,
    limit: int = 50,
    offset: int = 0,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.get_group_feed(group_id, limit, offset)

@router.post("/comments", response_model=CommentEntity, status_code=status.HTTP_201_CREATED)
@inject
def add_comment(
    data: CommentEntity,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.add_comment(data)

@router.get("/posts/{post_id}/comments", response_model=List[CommentEntity])
@inject
def get_comments(
    post_id: int,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.get_comments(post_id)

@router.post("/reports", response_model=ReportEntity, status_code=status.HTTP_201_CREATED)
@inject
def create_report(
    data: ReportEntity,
    controller: ForumsController = Depends(Provide[Container.forums_controller])
):
    return controller.create_report(data)
