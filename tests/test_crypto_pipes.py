import base64
import pytest
from cryptography.fernet import Fernet
from app.core.crypto.key_manager import IKeyManager
from app.core.crypto.crypto_pipes import FernetCipherPipe, FernetDecryptPipe

class MockKeyManager(IKeyManager):
    def __init__(self, key: str):
        self._key = key

    def get_master_key(self) -> str:
        return self._key

@pytest.fixture
def mock_key():
    return Fernet.generate_key().decode('utf-8')

@pytest.fixture
def key_manager(mock_key):
    return MockKeyManager(mock_key)

def test_cipher_pipe_encrypts_and_adds_prefix(key_manager):
    pipe = FernetCipherPipe(key_manager)
    original_text = "secret_data"
    
    encrypted = pipe.execute(original_text)
    
    # Debe tener el prefijo
    assert encrypted.startswith(FernetCipherPipe.VERSION_PREFIX)
    assert len(encrypted) > len(FernetCipherPipe.VERSION_PREFIX)

def test_cipher_pipe_handles_none_and_empty(key_manager):
    pipe = FernetCipherPipe(key_manager)
    assert pipe.execute(None) is None
    assert pipe.execute("") == ""

def test_decrypt_pipe_decrypts_versioned_data(key_manager):
    cipher_pipe = FernetCipherPipe(key_manager)
    decrypt_pipe = FernetDecryptPipe(key_manager)
    
    original_text = "secret_data"
    encrypted = cipher_pipe.execute(original_text)
    decrypted = decrypt_pipe.execute(encrypted)
    
    assert decrypted == original_text

def test_decrypt_pipe_handles_legacy_unversioned_data(key_manager, mock_key):
    decrypt_pipe = FernetDecryptPipe(key_manager)
    fernet = Fernet(mock_key.encode('utf-8'))
    
    original_text = "secret_data_legacy"
    # Legacy data just ferent encrypted and decoded as string (no base64 wrapping and no prefix)
    legacy_encrypted = fernet.encrypt(original_text.encode('utf-8')).decode('utf-8')
    
    decrypted = decrypt_pipe.execute(legacy_encrypted)
    assert decrypted == original_text

def test_decrypt_pipe_fallback_on_invalid_data(key_manager):
    decrypt_pipe = FernetDecryptPipe(key_manager)
    
    # Data that is not encrypted at all
    plain_text = "just_plain_text"
    decrypted = decrypt_pipe.execute(plain_text)
    
    assert decrypted == plain_text

def test_decrypt_pipe_handles_none_and_empty(key_manager):
    pipe = FernetDecryptPipe(key_manager)
    assert pipe.execute(None) is None
    assert pipe.execute("") == ""

def test_decrypt_pipe_fallback_on_corrupted_versioned_data(key_manager):
    decrypt_pipe = FernetDecryptPipe(key_manager)
    
    corrupted_data = FernetDecryptPipe.VERSION_PREFIX + "corrupted_base64_data_@@@"
    decrypted = decrypt_pipe.execute(corrupted_data)
    
    # Should fallback to returning raw data if it can't decrypt
    assert decrypted == corrupted_data
