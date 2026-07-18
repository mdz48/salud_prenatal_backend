import pytest
import os
from unittest.mock import MagicMock, patch

from shared_core.salud_prenatal_shared_core.vault_jwt_key_provider import VaultJwtKeyProvider

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("VAULT_ADDR", "http://fake-vault:8200")
    monkeypatch.setenv("VAULT_ROLE_ID", "fake-role-id")
    monkeypatch.setenv("VAULT_SECRET_ID", "fake-secret-id")

@pytest.fixture
def mock_hvac():
    with patch("hvac.Client") as mock_client_class:
        mock_instance = MagicMock()
        mock_instance.is_authenticated.return_value = True
        mock_client_class.return_value = mock_instance
        yield mock_instance

def test_vault_provider_algorithm():
    provider = VaultJwtKeyProvider()
    assert provider.algorithm == "RS256"

def test_vault_provider_missing_env_vars(monkeypatch):
    monkeypatch.delenv("VAULT_ROLE_ID", raising=False)
    provider = VaultJwtKeyProvider()
    with pytest.raises(RuntimeError, match="Faltan variables de entorno para Vault"):
        provider._get_client()

def test_vault_provider_auth_failure(mock_env, mock_hvac):
    mock_hvac.is_authenticated.return_value = False
    provider = VaultJwtKeyProvider()
    with pytest.raises(RuntimeError, match="Autenticación con Vault falló"):
        provider._get_client()

def test_vault_provider_get_signing_key(mock_env, mock_hvac):
    # Simular la respuesta de Vault para secret/jwt/private
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
        'data': {
            'data': {
                'private_key': 'fake-private-pem'
            }
        }
    }
    
    provider = VaultJwtKeyProvider()
    key = provider.get_signing_key()
    
    assert key == 'fake-private-pem'
    mock_hvac.secrets.kv.v2.read_secret_version.assert_called_once_with(path='jwt/private')

    # Verificar que el resultado se cachea (no hay llamada extra)
    key2 = provider.get_signing_key()
    assert key2 == 'fake-private-pem'
    assert mock_hvac.secrets.kv.v2.read_secret_version.call_count == 1

def test_vault_provider_get_verification_key(mock_env, mock_hvac):
    # Simular la respuesta de Vault para secret/jwt/public
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
        'data': {
            'data': {
                'public_key': 'fake-public-pem'
            }
        }
    }
    
    provider = VaultJwtKeyProvider()
    key = provider.get_verification_key()
    
    assert key == 'fake-public-pem'
    mock_hvac.secrets.kv.v2.read_secret_version.assert_called_once_with(path='jwt/public')

    # Verificar que el resultado se cachea (no hay llamada extra)
    key2 = provider.get_verification_key()
    assert key2 == 'fake-public-pem'
    assert mock_hvac.secrets.kv.v2.read_secret_version.call_count == 1

def test_vault_provider_key_not_found(mock_env, mock_hvac):
    # Simular respuesta sin llave
    mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
        'data': {
            'data': {}
        }
    }
    
    provider = VaultJwtKeyProvider()
    with pytest.raises(RuntimeError, match="Llave 'private_key' no encontrada"):
        provider.get_signing_key()

@pytest.mark.integration
def test_vault_provider_integration_end_to_end():
    """
    Test de integración (sólo se ejecuta si hay Vault vivo localmente).
    Verifica que se pueda firmar con la privada y validar con la pública.
    """
    import os
    if not os.getenv("RUN_VAULT_INTEGRATION_TESTS"):
        pytest.skip("Saltando test de integración de Vault. Setear RUN_VAULT_INTEGRATION_TESTS=1 para correrlo.")
        
    # Asume que Vault está corriendo y vault_bootstrap.py se ejecutó
    from jose import jwt
    
    # Necesitamos configurar las variables de entorno de prueba apuntando al auth
    # En un entorno real de integración, se pasan estas variables. Aquí asumiremos
    # que si RUN_VAULT_INTEGRATION_TESTS está configurado, el usuario ya configuró
    # VAULT_ROLE_ID y VAULT_SECRET_ID (idealmente los de auth, que pueden leer ambas o probar
    # instancias separadas).
    
    provider = VaultJwtKeyProvider()
    private_key = provider.get_signing_key()
    public_key = provider.get_verification_key()
    
    payload = {"sub": "test", "role": "admin"}
    token = jwt.encode(payload, private_key, algorithm="RS256")
    
    decoded = jwt.decode(token, public_key, algorithms=["RS256"])
    assert decoded["sub"] == "test"
    assert decoded["role"] == "admin"
