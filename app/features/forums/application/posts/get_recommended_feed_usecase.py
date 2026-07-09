from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.domain.feed_interleave import interleave

# Un anuncio de doctor tras cada AD_EVERY posts normales.
AD_EVERY = 4

class GetRecommendedFeedUseCase:
    """Posts de autoras del mismo cluster de riesgo que la usuaria, con anuncios
    de doctores intercalados. Sin cluster (o sin posts del cluster) cae al feed
    global; los anuncios se muestran a todas por igual."""

    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, user_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        profile = self.forums_repo.get_profile(user_id)
        posts = []
        if profile and profile.cluster_profile:
            posts = self.forums_repo.get_feed_by_cluster(profile.cluster_profile, limit, offset)
        if not posts:
            posts = self.forums_repo.get_global_feed(limit, offset)

        ads = self.forums_repo.get_ads(limit)
        return interleave(posts, ads, every=AD_EVERY)
