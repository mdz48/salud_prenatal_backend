from unittest.mock import MagicMock

from app.features.forums.infrastructure.controllers.posts_controller import PostsController
from app.features.forums.infrastructure.controllers.profiles_controller import ProfilesController
from app.features.forums.infrastructure.schemas.forums_schemas import PostCreate, ProfileCreate


def _posts_controller():
    create_uc = MagicMock()
    create_uc.execute.side_effect = lambda entity: entity  # devuelve la entidad tal cual
    return PostsController(create_uc, MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())


def test_create_post_usa_author_del_token():
    controller = _posts_controller()
    data = PostCreate(title="t", content="c")

    result = controller.create_post(data, author_id=42)

    assert result.author_id == 42


def test_create_profile_usa_user_id_del_token():
    create_uc = MagicMock()
    create_uc.execute.side_effect = lambda entity: entity
    controller = ProfilesController(create_uc, MagicMock())
    data = ProfileCreate(alias="ana")

    result = controller.create_profile(data, user_id=7)

    assert result.user_id == 7
