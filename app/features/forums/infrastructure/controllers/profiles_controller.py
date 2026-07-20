from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.application.profiles.create_profile_usecase import CreateProfileUseCase
from app.features.forums.application.profiles.get_profile_usecase import GetProfileUseCase
from app.features.forums.application.profiles.update_profile_usecase import UpdateProfileUseCase
from app.features.forums.application.profiles.get_profile_timeline_usecase import GetProfileTimelineUseCase
from app.features.forums.infrastructure.schemas.forums_schemas import (
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfileTimelineResponse, PostResponse
)
from app.features.forums.domain.ports import IImageStoragePort
from app.core.error_handlers import internal_error

class ProfilesController:
    def __init__(
        self,
        create_profile_uc: CreateProfileUseCase,
        get_profile_uc: GetProfileUseCase,
        update_profile_uc: UpdateProfileUseCase,
        get_profile_timeline_uc: GetProfileTimelineUseCase,
        image_storage: IImageStoragePort
    ):
        self.create_profile_uc = create_profile_uc
        self.get_profile_uc = get_profile_uc
        self.update_profile_uc = update_profile_uc
        self.get_profile_timeline_uc = get_profile_timeline_uc
        self.image_storage = image_storage

    def create_profile(self, data: ProfileCreate, user_id: int) -> ProfileResponse:
        try:
            entity = SocialProfileEntity(**data.model_dump(), user_id=user_id)
            result = self.create_profile_uc.execute(entity)
            return ProfileResponse.model_validate(result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise internal_error(e)

    def get_profile(self, user_id: int) -> ProfileResponse:
        try:
            profile = self.get_profile_uc.execute(user_id)
            if not profile:
                raise ValueError("Profile not found")
            return ProfileResponse.model_validate(profile)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise internal_error(e)

    def update_profile(self, data: ProfileUpdate, user_id: int) -> ProfileResponse:
        try:
            changes = data.model_dump(exclude_unset=True)
            result = self.update_profile_uc.execute(user_id, changes)
            return ProfileResponse.model_validate(result)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Alias already taken")
        except Exception as e:
            raise internal_error(e)

    def get_profile_timeline(self, user_id: int, limit: int = 50, offset: int = 0) -> ProfileTimelineResponse:
        try:
            profile, posts = self.get_profile_timeline_uc.execute(user_id, limit, offset)
            return ProfileTimelineResponse(
                profile=ProfileResponse.model_validate(profile),
                posts=[PostResponse.model_validate(p) for p in posts]
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise internal_error(e)

    def upload_profile_avatar(self, file_bytes: bytes, filename: str) -> str:
        try:
            return self.image_storage.upload_profile_avatar(file_bytes, filename)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise internal_error(e)
