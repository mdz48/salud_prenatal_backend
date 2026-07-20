import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.features.forums.infrastructure.controllers.posts_controller import PostsController
from app.features.forums.domain.ports import IImageStoragePort
from app.features.forums.application.posts.create_post_usecase import CreatePostUseCase
from app.features.forums.application.posts.get_global_feed_usecase import GetGlobalFeedUseCase
from app.features.forums.application.posts.get_group_feed_usecase import GetGroupFeedUseCase
from app.features.forums.application.posts.get_recommended_feed_usecase import GetRecommendedFeedUseCase
from app.features.forums.application.posts.add_comment_usecase import AddCommentUseCase
from app.features.forums.application.posts.get_comments_usecase import GetCommentsUseCase

@pytest.fixture
def mock_image_storage():
    return MagicMock(spec=IImageStoragePort)

@pytest.fixture
def controller(mock_image_storage):
    return PostsController(
        create_post_uc=MagicMock(spec=CreatePostUseCase),
        get_global_feed_uc=MagicMock(spec=GetGlobalFeedUseCase),
        get_group_feed_uc=MagicMock(spec=GetGroupFeedUseCase),
        add_comment_uc=MagicMock(spec=AddCommentUseCase),
        get_comments_uc=MagicMock(spec=GetCommentsUseCase),
        get_recommended_feed_uc=MagicMock(spec=GetRecommendedFeedUseCase),
        image_storage=mock_image_storage
    )

def test_upload_post_image_success(controller, mock_image_storage):
    mock_image_storage.upload_ad_image.return_value = "https://supabase.co/ads/123.webp"
    
    result = controller.upload_post_image(b"dummy_bytes", "test.jpg")
    
    assert result == "https://supabase.co/ads/123.webp"
    mock_image_storage.upload_ad_image.assert_called_once_with(b"dummy_bytes", "test.jpg")

def test_upload_post_image_value_error(controller, mock_image_storage):
    mock_image_storage.upload_ad_image.side_effect = ValueError("Invalid format")
    
    with pytest.raises(HTTPException) as exc_info:
        controller.upload_post_image(b"dummy_bytes", "test.txt")
        
    assert exc_info.value.status_code == 400
    assert "Invalid format" in exc_info.value.detail

def test_upload_post_image_runtime_error(controller, mock_image_storage):
    mock_image_storage.upload_ad_image.side_effect = RuntimeError("Supabase down")
    
    with pytest.raises(HTTPException) as exc_info:
        controller.upload_post_image(b"dummy_bytes", "test.jpg")
        
    assert exc_info.value.status_code == 500
    assert "error interno" in exc_info.value.detail.lower()
