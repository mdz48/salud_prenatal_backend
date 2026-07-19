from datetime import timedelta

from salud_prenatal_shared_core.time import now_cdmx
from app.forums.domain.ports import IForumsRepository, IAdEligibilityLookup
from app.forums.domain.post_entity import PostEntity
from app.forums.domain.exceptions import AdPermissionError, AdRateLimitError

WEEKLY_AD_LIMIT = 10

class CreatePostUseCase:
    def __init__(self, forums_repo: IForumsRepository, ad_eligibility: IAdEligibilityLookup):
        self.forums_repo = forums_repo
        self.ad_eligibility = ad_eligibility

    def execute(self, post: PostEntity) -> PostEntity:
        if post.is_ad:
            if not self.ad_eligibility.is_premium_active(post.author_id):
                raise AdPermissionError("La publicidad requiere suscripción premium activa")

            since = now_cdmx() - timedelta(days=7)
            if self.forums_repo.count_ads_by_author_since(post.author_id, since) >= WEEKLY_AD_LIMIT:
                raise AdRateLimitError("Límite semanal de anuncios alcanzado (10)")

        return self.forums_repo.create_post(post)
