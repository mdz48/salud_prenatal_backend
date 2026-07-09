"""Arma el árbol Composite de un hilo de foro (post + comentarios)."""
from app.features.forums.domain.forum_thread import CommentLeaf, PostComposite
from app.features.forums.domain.ports import IForumsRepository
from app.features.forums.domain.post_entity import PostEntity


class BuildPostThreadUseCase:
    def __init__(self, forums_repo: IForumsRepository):
        self.forums_repo = forums_repo

    def execute(self, post: PostEntity) -> PostComposite:
        composite = PostComposite(post)
        for comment in self.forums_repo.get_comments(post.post_id):
            composite.add(CommentLeaf(comment))
        return composite
