from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from app.core.dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from typing import List
from app.features.forums.infrastructure.schemas.forums_schemas import (
    PostCreate, PostResponse, CommentCreate, CommentResponse
)
from app.features.forums.infrastructure.controllers.posts_controller import PostsController
from app.features.users.domain.user_entity import UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Posts & Comments"])

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_post(
    data: PostCreate,
    current_user: UserEntity = Depends(get_current_user),
    controller: PostsController = Depends(Provide[Container.posts_controller])
):
    return controller.create_post(data, current_user.user_id)

@router.get("/posts/global", response_model=List[PostResponse])
@inject
def get_global_feed(
    limit: int = 50,
    offset: int = 0,
    controller: PostsController = Depends(Provide[Container.posts_controller])
):
    return controller.get_global_feed(limit, offset)

@router.get("/posts/recommended", response_model=List[PostResponse])
@inject
def get_recommended_feed(
    limit: int = 50,
    offset: int = 0,
    current_user: UserEntity = Depends(get_current_user),
    controller: PostsController = Depends(Provide[Container.posts_controller])
):
    return controller.get_recommended_feed(current_user.user_id, limit, offset)

@router.get("/groups/{group_id}/posts", response_model=List[PostResponse])
@inject
def get_group_feed(
    group_id: int,
    limit: int = 50,
    offset: int = 0,
    controller: PostsController = Depends(Provide[Container.posts_controller])
):
    return controller.get_group_feed(group_id, limit, offset)

@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
@inject
def add_comment(
    data: CommentCreate,
    current_user: UserEntity = Depends(get_current_user),
    controller: PostsController = Depends(Provide[Container.posts_controller])
):
    return controller.add_comment(data, current_user.user_id)

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
@inject
def get_comments(
    post_id: int,
    controller: PostsController = Depends(Provide[Container.posts_controller])
):
    return controller.get_comments(post_id)
