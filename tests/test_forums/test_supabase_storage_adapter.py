import pytest
import io
from unittest.mock import patch, MagicMock
from PIL import Image
from app.features.forums.infrastructure.adapters.supabase_storage_adapter import SupabaseStorageAdapter

@pytest.fixture
def adapter():
    return SupabaseStorageAdapter(
        supabase_url="http://mock-supabase.co",
        supabase_service_key="mock-key"
    )

def create_dummy_image(width, height, format="JPEG"):
    file_bytes = io.BytesIO()
    img = Image.new("RGB", (width, height), color="red")
    img.save(file_bytes, format=format)
    return file_bytes.getvalue()

def test_upload_ad_image_invalid_magic_bytes(adapter):
    with pytest.raises(ValueError, match="Formato de imagen no permitido"):
        adapter.upload_ad_image(b"invalid data here", "test.txt")

def test_upload_ad_image_too_small(adapter):
    with pytest.raises(ValueError, match="Archivo demasiado pequeño"):
        adapter.upload_ad_image(b"abc", "test.jpg")

@patch("httpx.post")
def test_upload_ad_image_success_jpeg(mock_post, adapter):
    dummy_bytes = create_dummy_image(100, 100, "JPEG")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    public_url = adapter.upload_ad_image(dummy_bytes, "test.jpg")
    
    assert "mock-supabase.co" in public_url
    assert public_url.endswith(".webp")
    assert mock_post.called
    
    args, kwargs = mock_post.call_args
    headers = kwargs["headers"]
    assert headers["Authorization"] == "Bearer mock-key"
    assert headers["Content-Type"] == "image/webp"

@patch("httpx.post")
def test_upload_ad_image_resizes_large_image(mock_post, adapter):
    large_bytes = create_dummy_image(1600, 800, "JPEG")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    public_url = adapter.upload_ad_image(large_bytes, "large.jpg")
    
    assert mock_post.called
    args, kwargs = mock_post.call_args
    uploaded_content = kwargs["content"]
    
    img = Image.open(io.BytesIO(uploaded_content))
    assert img.size[0] == 1200
    assert img.size[1] == 600

@patch("httpx.post")
def test_upload_profile_avatar_success(mock_post, adapter):
    # Crear una imagen rectangular de 800x600
    dummy_bytes = create_dummy_image(800, 600, "JPEG")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    public_url = adapter.upload_profile_avatar(dummy_bytes, "avatar.jpg")
    
    assert "mock-supabase.co" in public_url
    assert public_url.endswith(".webp")
    assert "/avatars/" in public_url
    assert mock_post.called
    
    args, kwargs = mock_post.call_args
    uploaded_content = kwargs["content"]
    
    # Comprobar que la imagen subida se recortó a 1:1 (400x400 px)
    img = Image.open(io.BytesIO(uploaded_content))
    assert img.size[0] == 400
    assert img.size[1] == 400
