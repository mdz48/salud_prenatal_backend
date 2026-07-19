# shared_core

Paquete Python común, instalado editable (`pip install -e ./shared_core`) por cada servicio.

**Vacío por ahora** — se llena en la **Sesión 1** extrayendo `app/core/` del monolito:

- `database.py` → `Base`, `TimestampMixin`, `get_engine`, `get_session_factory`, `get_db`
- `security.py` → JWT (`create_access_token`, `get_secret_key`, `ALGORITHM`), password hashing, `EncryptedString`
- `crypto/` → `key_manager`, `crypto_pipes` (Fernet)
- `time.py`, `enums.py`, `text.py`, `pregnancy_calculations.py`, `error_handlers.py`
- (Sesión 2) `auth_dependencies.py` → `Principal`, `get_current_user` (sin DB, desde claims), `RoleChecker`, `require_active_subscription`

Regla: `shared_core` NO importa nada de `app/features` ni de ningún `service_*`. Es hoja de dependencias.
