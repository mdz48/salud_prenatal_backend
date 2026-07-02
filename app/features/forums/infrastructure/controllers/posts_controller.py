from fastapi import HTTPException, status
from typing import List
from app.features.forums.domain.entities import PostEntity, CommentEntity
from app.features.forums.infrastructure.schemas.forums_schemas import (
    PostCreate, PostResponse, CommentCreate, CommentResponse
)
from app.features.forums.application.posts_usecases import (
    CreatePostUseCase, GetGlobalFeedUseCase, GetGroupFeedUseCase,
    AddCommentUseCase, GetCommentsUseCase
)

class PostsController:
    def __init__(
        self,
        create_post_uc: CreatePostUseCase,
        get_global_feed_uc: GetGlobalFeedUseCase,
        get_group_feed_uc: GetGroupFeedUseCase,
        add_comment_uc: AddCommentUseCase,
        get_comments_uc: GetCommentsUseCase
    ):
        self.create_post_uc = create_post_uc
        self.get_global_feed_uc = get_global_feed_uc
        self.get_group_feed_uc = get_group_feed_uc
        self.add_comment_uc = add_comment_uc
        self.get_comments_uc = get_comments_uc

    def create_post(self, data: PostCreate) -> PostResponse:
        try:
            entity = PostEntity(**data.model_dump())
            result = self.create_post_uc.execute(entity)
            return PostResponse.model_validate(result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_global_feed(self, limit: int = 50, offset: int = 0) -> List[PostResponse]:
        try:
            results = self.get_global_feed_uc.execute(limit, offset)
            return [PostResponse.model_validate(r) for r in results]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_group_feed(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostResponse]:
        try:
            results = self.get_group_feed_uc.execute(group_id, limit, offset)
            return [PostResponse.model_validate(r) for r in results]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def add_comment(self, data: CommentCreate) -> CommentResponse:
        try:
            entity = CommentEntity(**data.model_dump())
            result = self.add_comment_uc.execute(entity)
            return CommentResponse.model_validate(result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_comments(self, post_id: int) -> List[CommentResponse]:
        try:
            results = self.get_comments_uc.execute(post_id)
            return [CommentResponse.model_validate(r) for r in results]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
