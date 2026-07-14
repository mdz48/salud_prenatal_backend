from app.features.medical_record.domain.ports import ISocialClusterPort
from app.features.forums.infrastructure.repositories.forums_repository import ForumsRepository

class SocialClusterAdapter(ISocialClusterPort):
    """Propaga el cluster de riesgo del ML al perfil social del paciente.
    Si el usuario no tiene perfil social todavia, la escritura es un no-op."""

    def __init__(self, forums_repository: ForumsRepository):
        self.forums_repository = forums_repository

    def update_cluster(self, user_id: int, cluster: str) -> None:
        self.forums_repository.update_cluster_profile(user_id, cluster)
