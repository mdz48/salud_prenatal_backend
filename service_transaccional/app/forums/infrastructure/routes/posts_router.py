from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from salud_prenatal_shared_core.auth_dependencies import get_current_user
from fastapi import APIRouter, Depends, status
from typing import List
from app.forums.infrastructure.schemas.forums_schemas import (
    PostCreate, PostResponse, CommentCreate, CommentResponse
)
from app.forums.infrastructure.controllers.posts_controller import PostsController
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity

router = APIRouter(prefix="/forums", tags=["Forums - Posts & Comments"])


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_post(
    data: PostCreate,
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.posts_controller()
    return controller.create_post(data, current_user.user_id)


@router.get("/posts/global", response_model=List[PostResponse])
@close_db_after(Container)
def get_global_feed(
    limit: int = 50,
    offset: int = 0,
):
    controller = Container.posts_controller()
    return controller.get_global_feed(limit, offset)


@router.get("/posts/recommended", response_model=List[PostResponse])
@close_db_after(Container)
def get_recommended_feed(
    current_user: UserEntity = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    controller = Container.posts_controller()
    return controller.get_recommended_feed(current_user.user_id, limit, offset)


@router.get("/groups/{group_id}/posts", response_model=List[PostResponse])
@close_db_after(Container)
def get_group_feed(
    group_id: int,
    limit: int = 50,
    offset: int = 0,
):
    controller = Container.posts_controller()
    return controller.get_group_feed(group_id, limit, offset)


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def add_comment(
    data: CommentCreate,
    current_user: UserEntity = Depends(get_current_user),
):
    controller = Container.posts_controller()
    return controller.add_comment(data, current_user.user_id)


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
@close_db_after(Container)
def get_comments(
    post_id: int,
):
    controller = Container.posts_controller()
    return controller.get_comments(post_id)
