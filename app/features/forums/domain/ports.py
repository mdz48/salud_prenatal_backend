from abc import ABC, abstractmethod
from typing import List, Optional
from app.features.forums.domain.entities import (
    SocialProfileEntity,
    CommunityGroupEntity,
    PostEntity,
    CommentEntity,
    ReportEntity
)

class ForumsRepositoryPort(ABC):
    @abstractmethod
    def create_profile(self, profile: SocialProfileEntity) -> SocialProfileEntity:
        pass

    @abstractmethod
    def get_profile(self, user_id: int) -> Optional[SocialProfileEntity]:
        pass

    @abstractmethod
    def create_group(self, group: CommunityGroupEntity) -> CommunityGroupEntity:
        pass

    @abstractmethod
    def get_groups(self) -> List[CommunityGroupEntity]:
        pass

    @abstractmethod
    def create_post(self, post: PostEntity) -> PostEntity:
        pass

    @abstractmethod
    def get_global_feed(self, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        pass

    @abstractmethod
    def get_group_feed(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        pass

    @abstractmethod
    def add_comment(self, comment: CommentEntity) -> CommentEntity:
        pass

    @abstractmethod
    def get_comments(self, post_id: int) -> List[CommentEntity]:
        pass

    @abstractmethod
    def create_report(self, report: ReportEntity) -> ReportEntity:
        pass
