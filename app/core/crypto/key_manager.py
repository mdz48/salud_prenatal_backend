import os
from abc import ABC, abstractmethod

class IKeyManager(ABC):
    """Interfaz para la gestión de llaves de cifrado."""
    
    @abstractmethod
    def get_master_key(self) -> str:
        """Devuelve la llave maestra de cifrado."""
        pass

class EnvKeyManager(IKeyManager):
    """Gestor de llaves que obtiene la llave desde las variables de entorno."""
    
    def __init__(self, env_var_name: str = "ENCRYPTION_KEY"):
        self._env_var_name = env_var_name

    def get_master_key(self) -> str:
        key = os.getenv(self._env_var_name)
        if not key:
            raise ValueError(f"La variable de entorno {self._env_var_name} no está configurada.")
        return key
