from types import SimpleNamespace
from unittest.mock import MagicMock

from app.features.forums.infrastructure.adapters.author_role_adapter import AuthorRoleAdapter


def test_devuelve_role_value_del_usuario():
    user_repo = MagicMock()
    user_repo.get_by_id.return_value = SimpleNamespace(role=SimpleNamespace(value="doctor"))
    adapter = AuthorRoleAdapter(user_repo)

    assert adapter.get_role(5) == "doctor"


def test_usuario_inexistente_devuelve_none():
    user_repo = MagicMock()
    user_repo.get_by_id.return_value = None
    adapter = AuthorRoleAdapter(user_repo)

    assert adapter.get_role(999) is None
