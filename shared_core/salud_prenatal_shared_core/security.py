from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional
import os
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from functools import lru_cache
from sqlalchemy import TypeDecorator, String
from salud_prenatal_shared_core.crypto.key_manager import EnvKeyManager
from salud_prenatal_shared_core.crypto.crypto_pipes import FernetCipherPipe, FernetDecryptPipe
from salud_prenatal_shared_core.jwt_key_provider import get_jwt_key_provider

@lru_cache()
def get_secret_key() -> str:
    load_dotenv()
    key = os.getenv("SECRET_KEY")
    if not key:
        raise RuntimeError("SECRET_KEY no configurada; requerida para firmar JWTs.")
    return key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        # hash irreconocible (p.ej. cuentas anonimizadas con "deleted::...") = credencial invalida
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # La llave de firma la provee el Key Manager (port). Hoy es HS256/env; si el
    # key manager se externaliza, se cambia el provider, no esta función.
    provider = get_jwt_key_provider()
    return jwt.encode(to_encode, provider.get_signing_key(), algorithm=provider.algorithm)

@lru_cache()
def get_cipher_pipe():
    key_manager = EnvKeyManager()
    return FernetCipherPipe(key_manager)

@lru_cache()
def get_decrypt_pipe():
    key_manager = EnvKeyManager()
    return FernetDecryptPipe(key_manager)

class EncryptedString(TypeDecorator):
    """
    Encrypts string data on the way in, decrypts on the way out.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return get_cipher_pipe().execute(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return get_decrypt_pipe().execute(value)
