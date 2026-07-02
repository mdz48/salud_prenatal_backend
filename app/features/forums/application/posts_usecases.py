from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.entities import PostEntity, CommentEntity

class CreatePostUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, post: PostEntity) -> PostEntity:
        return self.forums_repo.create_post(post)

class GetGlobalFeedUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        return self.forums_repo.get_global_feed(limit, offset)

class GetGroupFeedUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        return self.forums_repo.get_group_feed(group_id, limit, offset)

class AddCommentUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, comment: CommentEntity) -> CommentEntity:
        return self.forums_repo.add_comment(comment)

class GetCommentsUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, post_id: int) -> List[CommentEntity]:
        return self.forums_repo.get_comments(post_id)
