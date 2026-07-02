from fastapi import HTTPException, status
from app.features.forums.domain.entities import (
    SocialProfileEntity,
    CommunityGroupEntity,
    PostEntity,
    CommentEntity,
    ReportEntity
)
from app.features.forums.application.forums_usecases import (
    CreateProfileUseCase,
    GetProfileUseCase,
    CreateGroupUseCase,
    GetGroupsUseCase,
    CreatePostUseCase,
    GetGlobalFeedUseCase,
    GetGroupFeedUseCase,
    AddCommentUseCase,
    GetCommentsUseCase,
    CreateReportUseCase
)

class ForumsController:
    def __init__(
        self,
        create_profile_uc: CreateProfileUseCase,
        get_profile_uc: GetProfileUseCase,
        create_group_uc: CreateGroupUseCase,
        get_groups_uc: GetGroupsUseCase,
        create_post_uc: CreatePostUseCase,
        get_global_feed_uc: GetGlobalFeedUseCase,
        get_group_feed_uc: GetGroupFeedUseCase,
        add_comment_uc: AddCommentUseCase,
        get_comments_uc: GetCommentsUseCase,
        create_report_uc: CreateReportUseCase
    ):
        self.create_profile_uc = create_profile_uc
        self.get_profile_uc = get_profile_uc
        self.create_group_uc = create_group_uc
        self.get_groups_uc = get_groups_uc
        self.create_post_uc = create_post_uc
        self.get_global_feed_uc = get_global_feed_uc
        self.get_group_feed_uc = get_group_feed_uc
        self.add_comment_uc = add_comment_uc
        self.get_comments_uc = get_comments_uc
        self.create_report_uc = create_report_uc

    def create_profile(self, data: SocialProfileEntity):
        try:
            return self.create_profile_uc.execute(data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_profile(self, user_id: int):
        try:
            profile = self.get_profile_uc.execute(user_id)
            if not profile:
                raise ValueError("Profile not found")
            return profile
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def create_group(self, data: CommunityGroupEntity):
        try:
            return self.create_group_uc.execute(data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_groups(self):
        try:
            return self.get_groups_uc.execute()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def create_post(self, data: PostEntity):
        try:
            return self.create_post_uc.execute(data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_global_feed(self, limit: int = 50, offset: int = 0):
        try:
            return self.get_global_feed_uc.execute(limit, offset)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_group_feed(self, group_id: int, limit: int = 50, offset: int = 0):
        try:
            return self.get_group_feed_uc.execute(group_id, limit, offset)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def add_comment(self, data: CommentEntity):
        try:
            return self.add_comment_uc.execute(data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_comments(self, post_id: int):
        try:
            return self.get_comments_uc.execute(post_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def create_report(self, data: ReportEntity):
        try:
            return self.create_report_uc.execute(data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
