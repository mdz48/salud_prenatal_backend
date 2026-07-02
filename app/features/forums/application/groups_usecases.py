from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.entities import CommunityGroupEntity

class CreateGroupUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, group: CommunityGroupEntity) -> CommunityGroupEntity:
        return self.forums_repo.create_group(group)

class GetGroupsUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self) -> List[CommunityGroupEntity]:
        return self.forums_repo.get_groups()
