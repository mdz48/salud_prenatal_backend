from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.post_entity import PostEntity

class GetRecommendedFeedUseCase:
    """Posts de autoras del mismo cluster de riesgo que la usuaria.
    Sin cluster asignado (o sin posts del cluster) cae al feed global."""

    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, user_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        profile = self.forums_repo.get_profile(user_id)
        if profile and profile.cluster_profile:
            posts = self.forums_repo.get_feed_by_cluster(profile.cluster_profile, limit, offset)
            if posts:
                return posts
        return self.forums_repo.get_global_feed(limit, offset)
