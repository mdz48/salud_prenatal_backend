from app.forums.domain.ports import IForumsRepository
from app.forums.domain.community_group_entity import CommunityGroupEntity

class CreateGroupUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, group: CommunityGroupEntity) -> CommunityGroupEntity:
        return self.forums_repo.create_group(group)
