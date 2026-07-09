"""Patrón Composite (ADR-13): árbol de un hilo de foro.

Trata de forma uniforme al post (nodo compuesto) y a sus comentarios (hojas)
mediante una interfaz común `ForumComponent`. Operaciones como `node_count` o
`to_dict` se resuelven recursivamente sobre el árbol.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.features.forums.domain.comment_entity import CommentEntity
from app.features.forums.domain.post_entity import PostEntity


class ForumComponent(ABC):
    @abstractmethod
    def node_count(self) -> int:
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        ...


class CommentLeaf(ForumComponent):
    def __init__(self, comment: CommentEntity):
        self.comment = comment

    def node_count(self) -> int:
        return 1

    def to_dict(self) -> dict:
        return {
            "type": "comment",
            "comment_id": self.comment.comment_id,
            "author_id": self.comment.author_id,
            "content": self.comment.content,
        }


class PostComposite(ForumComponent):
    def __init__(self, post: PostEntity):
        self.post = post
        self._children: List[ForumComponent] = []

    def add(self, child: ForumComponent) -> "PostComposite":
        self._children.append(child)
        return self

    @property
    def children(self) -> List[ForumComponent]:
        return list(self._children)

    def comment_count(self) -> int:
        return sum(child.node_count() for child in self._children)

    def node_count(self) -> int:
        return 1 + self.comment_count()

    def to_dict(self) -> dict:
        return {
            "type": "post",
            "post_id": self.post.post_id,
            "title": self.post.title,
            "author_id": self.post.author_id,
            "comment_count": self.comment_count(),
            "comments": [child.to_dict() for child in self._children],
        }
