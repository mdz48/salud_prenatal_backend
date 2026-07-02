from typing import List, Optional
from app.features.forums.domain.ports import ForumsRepositoryPort
from app.features.forums.domain.entities import (
    SocialProfileEntity,
    CommunityGroupEntity,
    PostEntity,
    CommentEntity,
    ReportEntity
)

class CreateProfileUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, profile: SocialProfileEntity) -> SocialProfileEntity:
        return self.forums_repo.create_profile(profile)

class GetProfileUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, user_id: int) -> Optional[SocialProfileEntity]:
        return self.forums_repo.get_profile(user_id)

class CreateGroupUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, group: CommunityGroupEntity) -> CommunityGroupEntity:
        return self.forums_repo.create_group(group)

class GetGroupsUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self) -> List[CommunityGroupEntity]:
        return self.forums_repo.get_groups()

class CreatePostUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, post: PostEntity) -> PostEntity:
        return self.forums_repo.create_post(post)

class GetGlobalFeedUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        return self.forums_repo.get_global_feed(limit, offset)

class GetGroupFeedUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        return self.forums_repo.get_group_feed(group_id, limit, offset)

class AddCommentUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, comment: CommentEntity) -> CommentEntity:
        return self.forums_repo.add_comment(comment)

class GetCommentsUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, post_id: int) -> List[CommentEntity]:
        return self.forums_repo.get_comments(post_id)

class CreateReportUseCase:
    def __init__(self, forums_repo: ForumsRepositoryPort):
        self.forums_repo = forums_repo

    def execute(self, report: ReportEntity) -> ReportEntity:
        return self.forums_repo.create_report(report)
