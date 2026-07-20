from fastapi import HTTPException, status
from typing import List
from app.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.forums.application.posts.get_global_feed_usecase import GetGlobalFeedUseCase
from app.forums.application.posts.get_group_feed_usecase import GetGroupFeedUseCase
from app.forums.application.posts.get_recommended_feed_usecase import GetRecommendedFeedUseCase
from app.forums.application.posts.add_comment_usecase import AddCommentUseCase
from app.forums.application.posts.get_comments_usecase import GetCommentsUseCase
from app.forums.domain.post_entity import PostEntity
from app.forums.domain.comment_entity import CommentEntity
from app.forums.domain.ports import IImageStoragePort
from app.forums.domain.exceptions import AdPermissionError, AdRateLimitError
from salud_prenatal_shared_core.error_handlers import internal_error
from app.forums.infrastructure.schemas.forums_schemas import (
    PostCreate, PostResponse, CommentCreate, CommentResponse
)

class PostsController:
    def __init__(
        self,
        create_post_uc: CreatePostUseCase,
        get_global_feed_uc: GetGlobalFeedUseCase,
        get_group_feed_uc: GetGroupFeedUseCase,
        add_comment_uc: AddCommentUseCase,
        get_comments_uc: GetCommentsUseCase,
        get_recommended_feed_uc: GetRecommendedFeedUseCase,
        image_storage: IImageStoragePort
    ):
        self.create_post_uc = create_post_uc
        self.get_global_feed_uc = get_global_feed_uc
        self.get_group_feed_uc = get_group_feed_uc
        self.add_comment_uc = add_comment_uc
        self.get_comments_uc = get_comments_uc
        self.get_recommended_feed_uc = get_recommended_feed_uc
        self.image_storage = image_storage

    def create_post(self, data: PostCreate, author_id: int) -> PostResponse:
        try:
            entity = PostEntity(**data.model_dump(), author_id=author_id)
            result = self.create_post_uc.execute(entity)
            return PostResponse.model_validate(result)
        except AdRateLimitError as e:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
        except AdPermissionError as e:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise internal_error(e)

    def get_global_feed(self, limit: int = 50, offset: int = 0) -> List[PostResponse]:
        try:
            results = self.get_global_feed_uc.execute(limit, offset)
            return [PostResponse.model_validate(r) for r in results]
        except Exception as e:
            raise internal_error(e)

    def get_recommended_feed(self, user_id: int, limit: int = 50, offset: int = 0) -> List[PostResponse]:
        try:
            results = self.get_recommended_feed_uc.execute(user_id, limit, offset)
            return [PostResponse.model_validate(r) for r in results]
        except Exception as e:
            raise internal_error(e)

    def get_group_feed(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostResponse]:
        try:
            results = self.get_group_feed_uc.execute(group_id, limit, offset)
            return [PostResponse.model_validate(r) for r in results]
        except Exception as e:
            raise internal_error(e)

    def add_comment(self, data: CommentCreate, author_id: int) -> CommentResponse:
        try:
            entity = CommentEntity(**data.model_dump(), author_id=author_id)
            result = self.add_comment_uc.execute(entity)
            return CommentResponse.model_validate(result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise internal_error(e)

    def get_comments(self, post_id: int) -> List[CommentResponse]:
        try:
            results = self.get_comments_uc.execute(post_id)
            return [CommentResponse.model_validate(r) for r in results]
        except Exception as e:
            raise internal_error(e)

    def upload_post_image(self, file_bytes: bytes, filename: str) -> str:
        try:
            return self.image_storage.upload_ad_image(file_bytes, filename)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise internal_error(e)
