from typing import List
from app.forums.domain.ports import IForumsRepository
from app.forums.domain.post_entity import PostEntity

class GetGlobalFeedUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        return self.forums_repo.get_global_feed(limit, offset)
