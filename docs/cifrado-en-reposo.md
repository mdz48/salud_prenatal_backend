# Encriptación de datos en reposo

**Ubicación:** [`shared_core/salud_prenatal_shared_core/crypto/`](../shared_core/salud_prenatal_shared_core/crypto) y [`security.py`](../shared_core/salud_prenatal_shared_core/security.py)

Los datos personales sensibles se guardan **cifrados en la base de datos**. El cifrado es transparente para el código de negocio: se aplica en la capa de tipos de SQLAlchemy.

## Cómo funciona

`EncryptedString` ([`security.py`](../shared_core/salud_prenatal_shared_core/security.py)) es un `TypeDecorator` de SQLAlchemy: cifra al escribir (`process_bind_param`) y descifra al leer (`process_result_value`). Declarar una columna cifrada es escribir un tipo distinto, nada más:

```python
name = Column(EncryptedString, nullable=False)
```

El algoritmo es **Fernet** (AES-128 en modo CBC con HMAC-SHA256 para autenticación), de la librería `cryptography`. La implementación sigue un patrón *pipes and filters* ([`crypto/crypto_pipes.py`](../shared_core/salud_prenatal_shared_core/crypto/crypto_pipes.py)):

- `FernetCipherPipe` — cifra y antepone el prefijo de versión `enc::v1::`.
- `FernetDecryptPipe` — reconoce el prefijo, descifra, y mantiene compatibilidad con los registros previos al versionado.

El prefijo de versión permite rotar el esquema criptográfico en el futuro sin migrar toda la tabla de golpe.

La llave la entrega `EnvKeyManager` ([`crypto/key_manager.py`](../shared_core/salud_prenatal_shared_core/crypto/key_manager.py)) desde `ENCRYPTION_KEY`, detrás de la interfaz `IKeyManager` — el mismo patrón de puerto que se usó para las llaves de JWT, de modo que sustituirlo por un gestor externo no obliga a tocar el código de cifrado.

## Qué está cifrado

| Servicio | Tabla / modelo | Columnas cifradas |
|---|---|---|
| `service_usuarios` | [`user_model.py`](../service_usuarios/app/users/infrastructure/models/user_model.py) | `name`, `last_name`, `phone` |
| `service_usuarios` | [`doctor_model.py`](../service_usuarios/app/users/infrastructure/models/doctor_model.py) | `professional_license`, `office` |
| `service_transaccional` | [`medical_record_model.py`](../service_transaccional/app/medical_record/infrastructure/models/medical_record_model.py) | `residence`, `education_level`, `marital_status` |
| `service_auth` | [`auth_readmodels.py`](../service_auth/app/auth/infrastructure/models/auth_readmodels.py) | `name`, `last_name` |
| `service_transaccional` | [`readmodels/users_readmodels.py`](../service_transaccional/app/readmodels/users_readmodels.py) | `name`, `last_name` |

Los *read models* de `auth` y `transaccional` reutilizan `EncryptedString` de `shared_core` precisamente para que todos los servicios lean la misma PII con la misma llave y el mismo formato.

## Contraseñas

Las contraseñas no se cifran: se **hashean** con **bcrypt** vía `passlib` ([`security.py`](../shared_core/salud_prenatal_shared_core/security.py)). El cifrado es reversible y el hash no — para credenciales, lo correcto es el hash.

## Pruebas

[`shared_core/tests/`](../shared_core/tests) cubre el pipeline de cifrado, los proveedores de llaves y las dependencias de autenticación.

---

Ver también: [gateway](gateway.md) · [métodos de pago](metodos-de-pago.md)
