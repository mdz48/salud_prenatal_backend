from fastapi import HTTPException, status
from typing import List
from app.features.forums.application.groups.create_group_usecase import CreateGroupUseCase
from app.features.forums.application.groups.get_groups_usecase import GetGroupsUseCase
from app.features.forums.application.groups.get_recommended_groups_usecase import GetRecommendedGroupsUseCase
from app.features.forums.domain.community_group_entity import CommunityGroupEntity
from app.features.forums.infrastructure.schemas.forums_schemas import GroupCreate, GroupResponse

class GroupsController:
    def __init__(
        self,
        create_group_uc: CreateGroupUseCase,
        get_groups_uc: GetGroupsUseCase,
        get_recommended_groups_uc: GetRecommendedGroupsUseCase
    ):
        self.create_group_uc = create_group_uc
        self.get_groups_uc = get_groups_uc
        self.get_recommended_groups_uc = get_recommended_groups_uc

    def create_group(self, data: GroupCreate, created_by: int) -> GroupResponse:
        try:
            entity = CommunityGroupEntity(**data.model_dump(), created_by=created_by)
            result = self.create_group_uc.execute(entity)
            return GroupResponse.model_validate(result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_groups(self) -> List[GroupResponse]:
        try:
            results = self.get_groups_uc.execute()
            return [GroupResponse.model_validate(r) for r in results]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_recommended_groups(self, user_id: int) -> List[GroupResponse]:
        try:
            results = self.get_recommended_groups_uc.execute(user_id)
            return [GroupResponse.model_validate(r) for r in results]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
