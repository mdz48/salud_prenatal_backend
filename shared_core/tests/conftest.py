import base64
import os

# Env de test ANTES de importar salud_prenatal_shared_core: security.py y
# crypto/key_manager.py leen estas variables al construir sus caches (@lru_cache).
#
# JWT_KEY_BACKEND se fuerza a vacío (no basta con setdefault): si el .env del
# repo lo trae en "vault", get_jwt_key_provider() intentaría hablarle a Vault y
# estas pruebas unitarias reventarían con RuntimeError.
os.environ["JWT_KEY_BACKEND"] = ""
os.environ.setdefault("SECRET_KEY", "test-secret")
# Llave Fernet válida y fija (32 bytes '0' en base64 urlsafe), solo para tests.
os.environ.setdefault(
    "ENCRYPTION_KEY", base64.urlsafe_b64encode(b"0" * 32).decode()
)
