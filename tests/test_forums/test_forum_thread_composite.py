"""ADR-13 Composite: árbol post + comentarios."""
from unittest.mock import MagicMock

from app.features.forums.application.posts.build_post_thread_usecase import BuildPostThreadUseCase
from app.features.forums.domain.comment_entity import CommentEntity
from app.features.forums.domain.forum_thread import CommentLeaf, PostComposite
from app.features.forums.domain.post_entity import PostEntity


def _post():
    return PostEntity(post_id=1, author_id=10, title="Hola", content="cuerpo")


def _comment(cid):
    return CommentEntity(comment_id=cid, post_id=1, author_id=20, content=f"c{cid}")


def test_composite_counts_recursively():
    composite = PostComposite(_post())
    composite.add(CommentLeaf(_comment(1))).add(CommentLeaf(_comment(2)))
    assert composite.comment_count() == 2
    assert composite.node_count() == 3  # post + 2 comentarios


def test_composite_to_dict_is_uniform():
    composite = PostComposite(_post()).add(CommentLeaf(_comment(1)))
    data = composite.to_dict()
    assert data["type"] == "post"
    assert data["comment_count"] == 1
    assert data["comments"][0]["type"] == "comment"
    assert data["comments"][0]["comment_id"] == 1


def test_build_post_thread_usecase():
    repo = MagicMock()
    repo.get_comments.return_value = [_comment(1), _comment(2), _comment(3)]
    usecase = BuildPostThreadUseCase(repo)

    thread = usecase.execute(_post())

    assert isinstance(thread, PostComposite)
    assert thread.comment_count() == 3
    repo.get_comments.assert_called_once_with(1)
