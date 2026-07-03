from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.social_profile_entity import SocialProfileEntity

class CreateProfileUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, profile: SocialProfileEntity) -> SocialProfileEntity:
        return self.forums_repo.create_profile(profile)
