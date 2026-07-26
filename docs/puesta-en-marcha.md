# Puesta en marcha

## Requisitos

Docker y Docker Compose. Para desarrollo fuera de contenedores, Python 3.11+.

## Todo el sistema

```bash
cp .env.example .env    # y llenar los valores
docker compose up --build
```

Esto levanta Traefik, Vault, PostgreSQL 16 y los cinco servicios.

| URL | Qué es |
|---|---|
| `http://localhost:8000` | API (edge de Traefik) |
| `http://localhost:8000/docs` | Swagger agregado de todos los servicios |
| `http://localhost:8090` | Dashboard de Traefik (solo local) |
| `http://localhost:8200` | Vault (solo local) |

> Los puertos 8001–8004 quedan publicados **únicamente para depuración local**. Golpearlos directamente evita el edge y, por tanto, la validación del JWT. En producción ([`docker-compose.vps.yml`](../docker-compose.vps.yml)) ningún servicio publica puerto.

## Un solo servicio en desarrollo

```bash
cd service_pagos && uvicorn main:app --reload --port 8003
```

## Instalar dependencias

```bash
.venv\Scripts\pip install -r service_pagos/requirements.txt
pip install -e ./shared_core
```

Cada servicio tiene su propio `requirements.txt`. Una librería nueva se agrega al del servicio que la usa, o al de `shared_core` si es transversal. Nunca se instala globalmente: siempre contra el `.venv`.

## Variables de entorno

Ver [`.env.example`](../.env.example) para la lista completa. Las esenciales:

| Variable | Para qué |
|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL compartida |
| `DATABASE_URL` | Override directo; si está definida ignora las `DB_*` (lo usan las pruebas con SQLite) |
| `SECRET_KEY` | Firma de JWT en HS256 (local y pruebas) |
| `ENCRYPTION_KEY` | Llave Fernet del cifrado en reposo (base64 urlsafe, 32 bytes) |
| `JWT_KEY_BACKEND=vault`, `VAULT_ADDR`, `VAULT_ROLE_ID_*`, `VAULT_SECRET_ID_*` | Firma RS256 con Vault (despliegue) |
| `STRIPE_PRIVATE_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_*` | Integración de pagos |
| `INTERNAL_SERVICE_TOKEN` | Secreto compartido para la llamada interna usuarios → transaccional |
| `ML_SERVICE_URL` | Servicio externo de predicción de riesgo de preeclampsia |
| `FRONTEND_URL` | Destino de los `success_url` / `cancel_url` de Stripe |

## Pruebas

Cada servicio tiene su propia suite y se ejecuta desde su directorio. No hay un comando único para todo el repositorio: los cinco servicios definen un paquete llamado `app`, así que recolectarlos juntos chocaría por nombre.

```bash
cd service_auth          && ..\.venv\Scripts\python -m pytest
cd service_usuarios      && ..\.venv\Scripts\python -m pytest
cd service_pagos         && ..\.venv\Scripts\python -m pytest
cd service_transaccional && ..\.venv\Scripts\python -m pytest
cd service_gateway       && ..\.venv\Scripts\python -m pytest
cd shared_core           && ..\.venv\Scripts\python -m pytest
```

Estado actual: **148 pruebas en verde, 1 omitida, 0 fallos** (auth 10, usuarios 24, pagos 20, transaccional 44, gateway 18, shared_core 32 + 1 omitida).

Las pruebas en `service_*/tests/` reflejan los nombres de las features (`tests/test_<feature>/`) y sustituyen los puertos del dominio por `MagicMock`, de modo que los casos de uso se prueban sin base de datos ni red. Las de integración llevan `@pytest.mark.integration` y ejecutan la aplicación real contra SQLite. El marker se declara en el [`pytest.ini`](../pytest.ini) de la raíz, que es la única configuración compartida del monorepo.

Cada `tests/conftest.py` fija el entorno de prueba (`DATABASE_URL` a SQLite, `SECRET_KEY`, `ENCRYPTION_KEY`) **antes** de importar `main` o `shared_core`, porque esos módulos cachean su configuración con `@lru_cache` en el primer uso. `service_auth` y `shared_core` además fuerzan `JWT_KEY_BACKEND=""`: son los que firman tokens, y si el `.env` del repo trae la configuración de Vault, las pruebas intentarían hablarle a un Vault que no está corriendo.

## Despliegue

Ver [despliegue en producción con Traefik y Vault](deploy-produccion-traefik-vault.md).
