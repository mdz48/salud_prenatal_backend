from app.features.forums.domain.ports import IForumsRepository, IAuthorRoleLookup
from app.features.forums.domain.post_entity import PostEntity

class CreatePostUseCase:
    def __init__(self, forums_repo: IForumsRepository, author_role_lookup: IAuthorRoleLookup):
        self.forums_repo = forums_repo
        self.author_role_lookup = author_role_lookup

    def execute(self, post: PostEntity) -> PostEntity:
        # Solo los doctores pueden publicar publicidad (is_ad).
        if post.is_ad and self.author_role_lookup.get_role(post.author_id) != "doctor":
            raise ValueError("Solo los doctores pueden publicar publicidad")
        return self.forums_repo.create_post(post)
