import pytest
from unittest.mock import MagicMock
from app.features.forums.application.profiles.create_profile_usecase import CreateProfileUseCase
from app.features.forums.application.groups.create_group_usecase import CreateGroupUseCase
from app.features.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.features.forums.application.reports.create_report_usecase import CreateReportUseCase
from app.features.forums.domain.social_profile_entity import SocialProfileEntity
from app.features.forums.domain.community_group_entity import CommunityGroupEntity
from app.features.forums.domain.post_entity import PostEntity
from app.features.forums.domain.report_entity import ReportEntity
from app.features.forums.domain.ports import IForumsRepository

@pytest.fixture
def mock_forums_repo():
    return MagicMock(spec=IForumsRepository)

def test_create_profile_usecase(mock_forums_repo):
    cluster_lookup = MagicMock()
    cluster_lookup.get_cluster_by_user_id.return_value = None
    usecase = CreateProfileUseCase(mock_forums_repo, cluster_lookup)
    profile_in = SocialProfileEntity(user_id=1, alias="testalias")
    mock_forums_repo.create_profile.return_value = profile_in
    
    result = usecase.execute(profile_in)
    
    mock_forums_repo.create_profile.assert_called_once_with(profile_in)
    assert result == profile_in
    assert result.user_id == 1

def test_create_group_usecase(mock_forums_repo):
    usecase = CreateGroupUseCase(mock_forums_repo)
    group_in = CommunityGroupEntity(name="Test Group", created_by=1)
    mock_forums_repo.create_group.return_value = group_in
    
    result = usecase.execute(group_in)
    
    mock_forums_repo.create_group.assert_called_once_with(group_in)
    assert result == group_in
    assert result.name == "Test Group"

def test_create_post_usecase(mock_forums_repo):
    role_lookup = MagicMock()
    usecase = CreatePostUseCase(mock_forums_repo, role_lookup)
    post_in = PostEntity(author_id=1, title="Test Post", content="This is a test post.")
    mock_forums_repo.create_post.return_value = post_in
    
    result = usecase.execute(post_in)
    
    mock_forums_repo.create_post.assert_called_once_with(post_in)
    assert result == post_in
    assert result.title == "Test Post"

def test_create_report_usecase(mock_forums_repo):
    usecase = CreateReportUseCase(mock_forums_repo)
    report_in = ReportEntity(reporter_id=1, post_id=1, reason="Spam")
    mock_forums_repo.create_report.return_value = report_in
    
    result = usecase.execute(report_in)
    
    mock_forums_repo.create_report.assert_called_once_with(report_in)
    assert result == report_in
    assert result.reason == "Spam"
