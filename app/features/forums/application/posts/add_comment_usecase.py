from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.comment_entity import CommentEntity

class AddCommentUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, comment: CommentEntity) -> CommentEntity:
        return self.forums_repo.add_comment(comment)
