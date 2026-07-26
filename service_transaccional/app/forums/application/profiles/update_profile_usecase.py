from app.forums.domain.ports import IForumsRepository
from app.forums.domain.social_profile_entity import SocialProfileEntity

class UpdateProfileUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, user_id: int, changes: dict) -> SocialProfileEntity:
        updated = self.forums_repo.update_profile(user_id, changes)
        if updated is None:
            raise ValueError("Profile not found")
        return updated
