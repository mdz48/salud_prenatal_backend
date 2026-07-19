import io
import uuid
import os
import httpx
from PIL import Image

class SupabaseStorageAdapter:
    def __init__(self, supabase_url: str = None, supabase_service_key: str = None):
        project_id = supabase_url or os.getenv("SUPABASE_URL", "")
        if project_id and not project_id.startswith("http"):
            self.base_url = f"https://{project_id}.supabase.co"
        else:
            self.base_url = project_id
        
        self.supabase_service_key = supabase_service_key or os.getenv("SUPABASE_SERVICE_KEY", "")
        self.bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "post-images")

    def _validate_image(self, file_bytes: bytes) -> None:
        if len(file_bytes) < 12:
            raise ValueError("Archivo demasiado pequeño o inválido")

        is_jpeg = file_bytes.startswith(b"\xff\xd8\xff")
        is_png = file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        is_webp = file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"

        if not (is_jpeg or is_png or is_webp):
            raise ValueError("Formato de imagen no permitido. Solo se permiten imágenes JPEG, PNG o WebP.")

    def _upload_to_supabase(self, processed_bytes: bytes, unique_filename: str) -> str:
        upload_url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{unique_filename}"

        headers = {
            "Authorization": f"Bearer {self.supabase_service_key}",
            "Content-Type": "image/webp",
            "x-upsert": "true"
        }

        try:
            response = httpx.post(upload_url, content=processed_bytes, headers=headers, timeout=30.0)
            if response.status_code != 200:
                raise RuntimeError(f"Error al subir a Supabase Storage: {response.text}")
        except Exception as e:
            raise RuntimeError(f"Error de conexión con Supabase Storage: {str(e)}")

        public_url = f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{unique_filename}"
        return public_url

    def upload_ad_image(self, file_bytes: bytes, filename: str) -> str:
        self._validate_image(file_bytes)

        try:
            img = Image.open(io.BytesIO(file_bytes))
            
            # Redimensionar si excede el ancho máximo de 1200px
            max_size = 1200
            width, height = img.size
            if width > max_size:
                ratio = max_size / float(width)
                new_height = int(float(height) * float(ratio))
                img = img.resize((max_size, new_height), Image.Resampling.LANCZOS)

            output_buffer = io.BytesIO()
            img.save(output_buffer, format="WEBP", quality=80)
            processed_bytes = output_buffer.getvalue()
        except Exception as e:
            raise ValueError(f"Error procesando la imagen: {str(e)}")

        unique_filename = f"ads/{uuid.uuid4()}.webp"
        return self._upload_to_supabase(processed_bytes, unique_filename)

    def upload_profile_avatar(self, file_bytes: bytes, filename: str) -> str:
        self._validate_image(file_bytes)

        try:
            img = Image.open(io.BytesIO(file_bytes))
            
            # Recorte cuadrado 1:1 centrado
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) / 2
            top = (height - min_dim) / 2
            right = (width + min_dim) / 2
            bottom = (height + min_dim) / 2
            img = img.crop((left, top, right, bottom))
            
            # Redimensionar a 400x400 px
            img = img.resize((400, 400), Image.Resampling.LANCZOS)

            output_buffer = io.BytesIO()
            img.save(output_buffer, format="WEBP", quality=80)
            processed_bytes = output_buffer.getvalue()
        except Exception as e:
            raise ValueError(f"Error procesando la imagen: {str(e)}")

        unique_filename = f"avatars/{uuid.uuid4()}.webp"
        return self._upload_to_supabase(processed_bytes, unique_filename)
