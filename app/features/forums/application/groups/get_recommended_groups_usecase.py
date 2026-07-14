from typing import List
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.community_group_entity import CommunityGroupEntity

class GetRecommendedGroupsUseCase:
    """Grupos etiquetados con el cluster de la usuaria; sin cluster o sin
    coincidencias devuelve todos los grupos."""

    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, user_id: int) -> List[CommunityGroupEntity]:
        profile = self.forums_repo.get_profile(user_id)
        if profile and profile.cluster_profile:
            groups = self.forums_repo.get_groups_by_cluster(profile.cluster_profile)
            if groups:
                return groups
        return self.forums_repo.get_groups()
