from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.comment_entity import CommentEntity

class GetCommentsUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, post_id: int) -> List[CommentEntity]:
        return self.forums_repo.get_comments(post_id)
