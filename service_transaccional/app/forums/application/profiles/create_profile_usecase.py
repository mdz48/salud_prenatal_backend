from app.forums.domain.ports import IForumsRepository, IPatientClusterLookup
from app.forums.domain.social_profile_entity import SocialProfileEntity

class CreateProfileUseCase:
    def __init__(self, forums_repo: IForumsRepository, cluster_lookup: IPatientClusterLookup):
        self.forums_repo = forums_repo
        self.cluster_lookup = cluster_lookup

    def execute(self, profile: SocialProfileEntity) -> SocialProfileEntity:
        # El cluster solo se deriva del ML; se ignora cualquier valor del cliente.
        profile.cluster_profile = self.cluster_lookup.get_cluster_by_user_id(profile.user_id)
        return self.forums_repo.create_profile(profile)
