from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.community_group_entity import CommunityGroupEntity

class GetGroupsUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self) -> List[CommunityGroupEntity]:
        return self.forums_repo.get_groups()
