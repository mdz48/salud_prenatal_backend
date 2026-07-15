from typing import List, Tuple
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.post_entity import PostEntity

class GetProfileTimelineUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, user_id: int, limit: int = 50, offset: int = 0) -> Tuple[SocialProfileEntity, List[PostEntity]]:
        profile = self.forums_repo.get_profile(user_id)
        if profile is None:
            raise ValueError("Profile not found")
        posts = self.forums_repo.get_posts_by_author(user_id, limit, offset)
        return profile, posts
