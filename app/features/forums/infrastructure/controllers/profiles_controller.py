from fastapi import HTTPException, status
from app.features.forums.domain.entities import SocialProfileEntity
from app.features.forums.infrastructure.schemas.forums_schemas import ProfileCreate, ProfileResponse
from app.features.forums.application.profiles_usecases import CreateProfileUseCase, GetProfileUseCase

class ProfilesController:
    def __init__(
        self,
        create_profile_uc: CreateProfileUseCase,
        get_profile_uc: GetProfileUseCase
    ):
        self.create_profile_uc = create_profile_uc
        self.get_profile_uc = get_profile_uc

    def create_profile(self, data: ProfileCreate) -> ProfileResponse:
        try:
            entity = SocialProfileEntity(**data.model_dump())
            result = self.create_profile_uc.execute(entity)
            return ProfileResponse.model_validate(result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_profile(self, user_id: int) -> ProfileResponse:
        try:
            profile = self.get_profile_uc.execute(user_id)
            if not profile:
                raise ValueError("Profile not found")
            return ProfileResponse.model_validate(profile)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
