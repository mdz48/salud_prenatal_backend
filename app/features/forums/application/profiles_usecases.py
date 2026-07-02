from typing import Optional
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.entities import SocialProfileEntity

class CreateProfileUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, profile: SocialProfileEntity) -> SocialProfileEntity:
        return self.forums_repo.create_profile(profile)

class GetProfileUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, user_id: int) -> Optional[SocialProfileEntity]:
        return self.forums_repo.get_profile(user_id)
