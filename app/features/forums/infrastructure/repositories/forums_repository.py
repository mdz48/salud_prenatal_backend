from typing import List, Optional
from sqlalchemy.orm import Session
from app.features.forums.domain.entities import (
    SocialProfileEntity,
    CommunityGroupEntity,
    PostEntity,
    CommentEntity,
    ReportEntity
)
from app.features.forums.infrastructure.models.forums_model import (
    SocialProfileModel,
    CommunityGroupModel,
    PostModel,
    CommentModel,
    ReportModel
)

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

    def get_group_feed(self, group_id: int, limit: int = 50, offset: int = 0) -> List[PostEntity]:
        db_posts = self.db.query(PostModel).filter(PostModel.group_id == group_id).order_by(PostModel.created_at.desc()).offset(offset).limit(limit).all()
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
