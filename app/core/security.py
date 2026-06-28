from datetime import datetime, timedelta
from typing import Optional
import os
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from sqlalchemy import TypeDecorator, String
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY.encode()) if ENCRYPTION_KEY else None

class EncryptedString(TypeDecorator):
    """
    Encrypts string data on the way in, decrypts on the way out.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if fernet is None:
            raise ValueError("ENCRYPTION_KEY is not set in environment variables.")
        encrypted_bytes = fernet.encrypt(value.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if fernet is None:
            return value
        try:
            decrypted_bytes = fernet.decrypt(value.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            return value