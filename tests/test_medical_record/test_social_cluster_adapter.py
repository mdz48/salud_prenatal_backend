from unittest.mock import MagicMock

from app.features.medical_record.infrastructure.adapters.social_cluster_adapter import SocialClusterAdapter


def test_delega_en_forums_repository():
    forums_repo = MagicMock()
    adapter = SocialClusterAdapter(forums_repo)

    adapter.update_cluster(7, "3")

    forums_repo.update_cluster_profile.assert_called_once_with(7, "3")
