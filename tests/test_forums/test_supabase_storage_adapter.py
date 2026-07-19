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

def test_upload_image_invalid_magic_bytes(adapter):
    with pytest.raises(ValueError, match="Formato de imagen no permitido"):
        adapter.upload_image(b"invalid data here", "test.txt")

def test_upload_image_too_small(adapter):
    with pytest.raises(ValueError, match="Archivo demasiado pequeño"):
        adapter.upload_image(b"abc", "test.jpg")

@patch("httpx.post")
def test_upload_image_success_jpeg(mock_post, adapter):
    # Generar bytes válidos de una imagen JPEG
    dummy_bytes = create_dummy_image(100, 100, "JPEG")
    
    # Mockear respuesta de HTTPX
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    public_url = adapter.upload_image(dummy_bytes, "test.jpg")
    
    assert "mock-supabase.co" in public_url
    assert public_url.endswith(".webp")
    assert mock_post.called
    
    # Verificar los headers de la petición a Supabase
    args, kwargs = mock_post.call_args
    headers = kwargs["headers"]
    assert headers["Authorization"] == "Bearer mock-key"
    assert headers["Content-Type"] == "image/webp"

@patch("httpx.post")
def test_upload_image_success_png(mock_post, adapter):
    dummy_bytes = create_dummy_image(100, 100, "PNG")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    public_url = adapter.upload_image(dummy_bytes, "test.png")
    
    assert "mock-supabase.co" in public_url
    assert public_url.endswith(".webp")
    assert mock_post.called

@patch("httpx.post")
def test_upload_image_resizes_large_image(mock_post, adapter):
    # Creamos una imagen grande de 1600x800
    large_bytes = create_dummy_image(1600, 800, "JPEG")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Espiar la redimensión de Pillow interceptando la subida
    public_url = adapter.upload_image(large_bytes, "large.jpg")
    
    # Verificar que el contenido subido sea una imagen válida y que sus dimensiones se hayan reducido
    assert mock_post.called
    args, kwargs = mock_post.call_args
    uploaded_content = kwargs["content"]
    
    # Abrir la imagen subida con Pillow para verificar el tamaño
    img = Image.open(io.BytesIO(uploaded_content))
    assert img.size[0] == 1200 # Redimensionada al ancho máximo
    assert img.size[1] == 600  # Manteniendo proporción de aspecto 2:1

@patch("httpx.post")
def test_upload_image_failure_response(mock_post, adapter):
    dummy_bytes = create_dummy_image(100, 100, "JPEG")
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bucket not found"
    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError, match="Error al subir a Supabase Storage"):
        adapter.upload_image(dummy_bytes, "test.jpg")
