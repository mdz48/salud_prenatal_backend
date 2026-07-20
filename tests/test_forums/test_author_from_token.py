from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.infrastructure.controllers.posts_controller import PostsController
from app.features.forums.infrastructure.controllers.profiles_controller import ProfilesController
from app.features.forums.infrastructure.schemas.forums_schemas import (
    PostCreate, ProfileCreate, ProfileUpdate, ProfileTimelineResponse
)


def _posts_controller():
    create_uc = MagicMock()
    create_uc.execute.side_effect = lambda entity: entity  # devuelve la entidad tal cual
    return PostsController(create_uc, MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock())


def test_create_post_usa_author_del_token():
    controller = _posts_controller()
    data = PostCreate(title="t", content="c")

    result = controller.create_post(data, author_id=42)

    assert result.author_id == 42


def test_create_profile_usa_user_id_del_token():
    create_uc = MagicMock()
    create_uc.execute.side_effect = lambda entity: entity
    controller = ProfilesController(create_uc, MagicMock(), MagicMock(), MagicMock(), MagicMock())
    data = ProfileCreate(alias="ana")

    result = controller.create_profile(data, user_id=7)

    assert result.user_id == 7


def test_update_profile_usa_user_id_del_token():
    update_uc = MagicMock()
    update_uc.execute.side_effect = lambda user_id, changes: SocialProfileEntity(user_id=user_id, **changes)
    controller = ProfilesController(MagicMock(), MagicMock(), update_uc, MagicMock(), MagicMock())
    data = ProfileUpdate(bio="hola")

    result = controller.update_profile(data, user_id=7)

    update_uc.execute.assert_called_once_with(7, {"bio": "hola"})
    assert result.user_id == 7
    assert result.bio == "hola"


def test_update_profile_no_encontrado_da_404():
    update_uc = MagicMock()
    update_uc.execute.side_effect = ValueError("Profile not found")
    controller = ProfilesController(MagicMock(), MagicMock(), update_uc, MagicMock(), MagicMock())

    with pytest.raises(HTTPException) as exc_info:
        controller.update_profile(ProfileUpdate(bio="hola"), user_id=404)

    assert exc_info.value.status_code == 404


def test_update_profile_alias_duplicado_da_409():
    update_uc = MagicMock()
    update_uc.execute.side_effect = IntegrityError("stmt", "params", Exception("UNIQUE constraint failed"))
    controller = ProfilesController(MagicMock(), MagicMock(), update_uc, MagicMock(), MagicMock())

    with pytest.raises(HTTPException) as exc_info:
        controller.update_profile(ProfileUpdate(alias="taken"), user_id=1)

    assert exc_info.value.status_code == 409


def test_get_profile_timeline_devuelve_perfil_y_posts():
    timeline_uc = MagicMock()
    profile = SocialProfileEntity(user_id=3, alias="ana")
    posts = [PostEntity(post_id=1, author_id=3, title="t", content="c")]
    timeline_uc.execute.return_value = (profile, posts)
    controller = ProfilesController(MagicMock(), MagicMock(), MagicMock(), timeline_uc, MagicMock())

    result = controller.get_profile_timeline(3, 50, 0)

    timeline_uc.execute.assert_called_once_with(3, 50, 0)
    assert result.profile.user_id == 3
    assert len(result.posts) == 1
    assert result.posts[0].post_id == 1


def test_get_profile_timeline_no_encontrado_da_404():
    timeline_uc = MagicMock()
    timeline_uc.execute.side_effect = ValueError("Profile not found")
    controller = ProfilesController(MagicMock(), MagicMock(), MagicMock(), timeline_uc, MagicMock())

    with pytest.raises(HTTPException) as exc_info:
        controller.get_profile_timeline(404, 50, 0)

    assert exc_info.value.status_code == 404
