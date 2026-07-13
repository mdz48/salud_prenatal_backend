from typing import List, Optional
from sqlalchemy.orm import Session
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.community_group_entity import CommunityGroupEntity
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.domain.comment_entity import CommentEntity
from app.features.forums.domain.report_entity import ReportEntity
from app.features.forums.infrastructure.models.social_profile_model import SocialProfileModel
from app.features.forums.infrastructure.models.community_group_model import CommunityGroupModel
from app.features.forums.infrastructure.models.post_model import PostModel
from app.features.forums.infrastructure.models.comment_model import CommentModel
from app.features.forums.infrastructure.models.report_model import ReportModel

class ForumsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_profile(self, profile: SocialProfileEntity) -> SocialProfileEntity:
        db_profile = SocialProfileModel(**profile.model_dump(exclude_unset=True))
        try:
            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)
            return SocialProfileEntity.model_validate(db_profile)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_profile(self, user_id: int) -> Optional[SocialProfileEntity]:
        db_profile = self.db.query(SocialProfileModel).filter(SocialProfileModel.user_id == user_id).first()
        if db_profile:
            return SocialProfileEntity.model_validate(db_profile)
        return None

    def update_cluster_profile(self, user_id: int, cluster: str) -> None:
        db_profile = self.db.query(SocialProfileModel).filter(SocialProfileModel.user_id == user_id).first()
        if not db_profile:
            return
        try:
            db_profile.cluster_profile = cluster
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def update_profile(self, user_id: int, changes: dict) -> Optional[SocialProfileEntity]:
        db_profile = self.db.query(SocialProfileModel).filter(SocialProfileModel.user_id == user_id).first()
        if not db_profile:
            return None
        for key, value in changes.items():
            if key not in {"user_id", "cluster_profile"}:
                setattr(db_profile, key, value)
        try:
            self.db.commit()
            self.db.refresh(db_profile)
            return SocialProfileEntity.model_validate(db_profile)
        except Exception as e:
            self.db.rollback()
            raise e

    def create_group(self, group: CommunityGroupEntity) -> CommunityGroupEntity:
        db_group = CommunityGroupModel(**group.model_dump(exclude={"group_id"}, exclude_unset=True))
        try:
            self.db.add(db_group)
            self.db.commit()
            self.db.refresh(db_group)
            return CommunityGroupEntity.model_validate(db_group)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_groups(self) -> List[CommunityGroupEntity]:
        db_groups = self.db.query(CommunityGroupModel).all()
        return [CommunityGroupEntity.model_validate(g) for g in db_groups]

    def get_groups_by_cluster(self, cluster: str) -> List[CommunityGroupEntity]:
        db_groups = self.db.query(CommunityGroupModel).filter(CommunityGroupModel.cluster_tag == cluster).all()
        return [CommunityGroupEntity.model_validate(g) for g in db_groups]

    def create_post(self, post: PostEntity) -> PostEntity:
        db_post = PostModel(**post.model_dump(exclude={"post_id"}, exclude_unset=True))
        try:
            self.db.add(db_post)
            self.db.commit()
            self.db.refresh(db_post)
            return PostEntity.model_validate(db_post)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_global_feed(self, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        db_posts = self.db.query(PostModel).filter(PostModel.group_id == None).order_by(PostModel.created_at.desc()).offset(offset).limit(limit).all()
        return [PostEntity.model_validate(p) for p in db_posts]

    def get_ads(self, limit: int = 20) -> List[PostEntity]:
        db_posts = (
            self.db.query(PostModel)
            .filter(PostModel.is_ad == True, PostModel.group_id == None)
            .order_by(PostModel.created_at.desc())
            .limit(limit).all()
        )
        return [PostEntity.model_validate(p) for p in db_posts]

    def get_feed_by_cluster(self, cluster: str, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        db_posts = (
            self.db.query(PostModel)
            .join(SocialProfileModel, SocialProfileModel.user_id == PostModel.author_id)
            .filter(SocialProfileModel.cluster_profile == cluster, PostModel.group_id == None, PostModel.is_ad == False)
            .order_by(PostModel.created_at.desc())
            .offset(offset).limit(limit).all()
        )
        return [PostEntity.model_validate(p) for p in db_posts]

    def count_ads_by_author_since(self, author_id: int, since) -> int:
        return (
            self.db.query(PostModel)
            .filter(PostModel.author_id == author_id, PostModel.is_ad == True, PostModel.created_at >= since)
            .count()
        )

    def get_group_feed(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        db_posts = self.db.query(PostModel).filter(PostModel.group_id == group_id).order_by(PostModel.created_at.desc()).offset(offset).limit(limit).all()
        return [PostEntity.model_validate(p) for p in db_posts]

    def get_posts_by_author(self, author_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        db_posts = (
            self.db.query(PostModel)
            .filter(PostModel.author_id == author_id)
            .order_by(PostModel.created_at.desc())
            .offset(offset).limit(limit).all()
        )
        return [PostEntity.model_validate(p) for p in db_posts]

    def add_comment(self, comment: CommentEntity) -> CommentEntity:
        db_comment = CommentModel(**comment.model_dump(exclude={"comment_id"}, exclude_unset=True))
        try:
            self.db.add(db_comment)
            self.db.commit()
            self.db.refresh(db_comment)
            return CommentEntity.model_validate(db_comment)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_comments(self, post_id: int) -> List[CommentEntity]:
        db_comments = self.db.query(CommentModel).filter(CommentModel.post_id == post_id).order_by(CommentModel.created_at.asc()).all()
        return [CommentEntity.model_validate(c) for c in db_comments]

    def create_report(self, report: ReportEntity) -> ReportEntity:
        db_report = ReportModel(**report.model_dump(exclude={"report_id"}, exclude_unset=True))
        try:
            self.db.add(db_report)
            self.db.commit()
            self.db.refresh(db_report)
            return ReportEntity.model_validate(db_report)
        except Exception as e:
            self.db.rollback()
            raise e
