from abc import ABC, abstractmethod
from typing import Any
import base64
from cryptography.fernet import Fernet, InvalidToken
from app.core.crypto.key_manager import IKeyManager

class PipelineFilter(ABC):
    """Interfaz base para los pasos del pipeline."""
    @abstractmethod
    def execute(self, data: str, context: dict[str, Any]) -> str:
        pass

class FernetCipherPipe(PipelineFilter):
    """Pipeline que cifra un string usando Fernet y añade versionado."""
    
    VERSION_PREFIX = "enc::v1::"
    
    def __init__(self, key_manager: IKeyManager):
        self._key_manager = key_manager
        
    def execute(self, data: str, context: dict[str, Any] = None) -> str:
        if not data:
            return data
            
        master_key = self._key_manager.get_master_key()
        fernet = Fernet(master_key.encode('utf-8'))
        
        encrypted_bytes = fernet.encrypt(data.encode('utf-8'))
        # Convertimos los bytes a base64 string
        encoded_str = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return f"{self.VERSION_PREFIX}{encoded_str}"

class FernetDecryptPipe(PipelineFilter):
    """Pipeline que descifra un string usando Fernet considerando el versionado."""
    
    VERSION_PREFIX = "enc::v1::"
    
    def __init__(self, key_manager: IKeyManager):
        self._key_manager = key_manager
        
    def execute(self, data: str, context: dict[str, Any] = None) -> str:
        if not data:
            return data
            
        master_key = self._key_manager.get_master_key()
        fernet = Fernet(master_key.encode('utf-8'))
        
        # Check if it has the new version prefix
        if data.startswith(self.VERSION_PREFIX):
            encoded_str = data[len(self.VERSION_PREFIX):]
            try:
                encrypted_bytes = base64.b64decode(encoded_str)
                decrypted_bytes = fernet.decrypt(encrypted_bytes)
                return decrypted_bytes.decode('utf-8')
            except (InvalidToken, ValueError, TypeError):
                # Si falla el descifrado a pesar del prefijo, devolvemos raw por seguridad/fallback
                return data
        else:
            # Legacy fallback: Intentar descifrar sin versionado
            # En la implementacion original, el string era casteado directo sin base64 extra
            try:
                decrypted_bytes = fernet.decrypt(data.encode('utf-8'))
                return decrypted_bytes.decode('utf-8')
            except InvalidToken:
                # Si no se pudo descifrar (posiblemente porque ya estaba en plano), retornamos en plano
                return data
