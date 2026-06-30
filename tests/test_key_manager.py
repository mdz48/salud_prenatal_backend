import os
import pytest
from unittest.mock import patch
from app.core.crypto.key_manager import EnvKeyManager

def test_env_key_manager_returns_key():
    mock_key = "test_super_secret_key"
    manager = EnvKeyManager(env_var_name="TEST_ENCRYPTION_KEY")
    
    with patch.dict(os.environ, {"TEST_ENCRYPTION_KEY": mock_key}):
        key = manager.get_master_key()
        assert key == mock_key

def test_env_key_manager_raises_error_if_not_set():
    manager = EnvKeyManager(env_var_name="NON_EXISTENT_KEY")
    
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="La variable de entorno NON_EXISTENT_KEY no está configurada."):
            manager.get_master_key()
