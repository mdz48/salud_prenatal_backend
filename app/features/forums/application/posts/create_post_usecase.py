from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.post_entity import PostEntity

class CreatePostUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, post: PostEntity) -> PostEntity:
        return self.forums_repo.create_post(post)
