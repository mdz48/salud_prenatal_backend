# Salud Prenatal — Backend

Backend de una plataforma de salud prenatal, construido como **monorepo de 5 microservicios FastAPI** sobre una **PostgreSQL compartida**, con **Traefik** como edge router, **HashiCorp Vault** para las llaves de firma de JWT y **Stripe** para los pagos.

Cada servicio es una aplicación FastAPI independiente, con su propio `Dockerfile`, sus propias dependencias, su propio contenedor de inyección de dependencias y su propia suite de pruebas.

---

## 1. Los tres rasgos obligatorios

Índice directo a los tres puntos solicitados. Cada uno tiene su documento con el detalle.

| Rasgo | Dónde vive | Documento |
|---|---|---|
| **Gateway** | `service_gateway/` + [`docker-compose.yml`](docker-compose.yml) — Traefik + ForwardAuth | **[docs/gateway.md](docs/gateway.md)** |
| **Encriptación de datos en reposo** | [`shared_core/.../crypto/`](shared_core/salud_prenatal_shared_core/crypto) + [`security.py`](shared_core/salud_prenatal_shared_core/security.py) | **[docs/cifrado-en-reposo.md](docs/cifrado-en-reposo.md)** |
| **Métodos de pago** | `service_pagos/` — Stripe: tarjeta recurrente, tarjeta única, OXXO y SPEI | **[docs/metodos-de-pago.md](docs/metodos-de-pago.md)** |

En resumen: la identidad se valida **una sola vez en el edge** y viaja como cabeceras `X-User-*` que Traefik borra si las manda el cliente; la PII se guarda cifrada con **Fernet** mediante un tipo `EncryptedString` de SQLAlchemy; y los pagos soportan **cuatro métodos** vía Stripe, con webhook idempotente respaldado por un libro mayor de transacciones.

---

## 2. Mapa del repositorio

```
salud_prenatal_backend/
├── docker-compose.yml            # Orquestación local: Traefik + Vault + Postgres + 5 servicios
├── docker-compose.staging.yml    # Overlay de staging
├── docker-compose.vps.yml        # Overlay de producción (sin puertos expuestos, TLS)
├── traefik-dynamic.yml           # Configuración dinámica de Traefik (TLS)
├── .env.example                  # Plantilla de variables de entorno
├── pytest.ini                    # Config de pytest compartida (markers)
│
├── service_gateway/              # Gateway: validación JWT en el edge (ForwardAuth) + docs
├── service_auth/                 # Emisión de JWT (login / refresh)
├── service_usuarios/             # Usuarios, doctores, pacientes, recepcionistas
├── service_pagos/                # Suscripciones y pagos (Stripe)
├── service_transaccional/        # Citas, consultas, expediente, bitácora, foros, chat, notificaciones
├── shared_core/                  # Paquete instalable compartido por todos los servicios
│
├── docs/                         # Documentación: ADRs, arquitectura, guías de integración
├── scripts/                      # Utilidades: seed de DB, bootstrap de Vault, smoke E2E, índices
└── graphify-out/                 # Grafo de conocimiento del código (generado)
```

No hay `main.py`, `requirements.txt` ni `Dockerfile` en la raíz: **cada servicio trae los suyos**. El monolito original del que partió el proyecto fue retirado por completo tras la migración; todo el código en ejecución vive bajo `service_*/` y `shared_core/`.

---

## 3. Arquitectura general

Todo el tráfico externo entra por **Traefik** en un único puerto. Antes de enrutar cualquier petición, Traefik consulta al **gateway** (patrón *ForwardAuth*), que valida el JWT una sola vez y devuelve la identidad como cabeceras. Los servicios de negocio nunca decodifican tokens.

```
   Cliente ──▶ TRAEFIK (edge :8000) ──ForwardAuth──▶ service_gateway ──▶ VAULT
                      │                              /validate            (RS256)
                      │                              /validate/strict
                      │              devuelve X-User-Id / -Email / -Role /
                      │                       X-Subscription-Status / -Period-End
                      ▼
        ┌────────┬─────────┬────────┬──────────────┐
        ▼        ▼         ▼        ▼              │
      auth    usuarios   pagos   transaccional     │  pagos ──▶ Stripe
      :8001    :8002     :8003      :8004          │  transaccional ──▶ ML service
        └────────┴─────────┴────────┘              │
                     ▼
        PostgreSQL 16 (compartida por todos)
```

### Principios de diseño

- **La base de datos compartida es el contrato.** Cada servicio declara sus **propios** modelos ORM para las tablas que necesita. Ningún servicio importa código de otro servicio.
- **La identidad se valida una sola vez, en el edge.** Los servicios de negocio no decodifican JWT ni consultan la base de datos para saber quién es el usuario: leen las cabeceras `X-User-*` que Traefik inyecta.
- **Traefik borra las cabeceras `X-User-*` que envíe el cliente**, de modo que no se pueden falsificar desde fuera.
- **Lo verdaderamente común vive en `shared_core`**, instalado como paquete (`pip install -e ./shared_core`), no copiado entre servicios.

### Servicios

| Servicio | Carpeta | Puerto | Prefijos de ruta | Responsabilidad |
|---|---|---|---|---|
| **gateway** | `service_gateway/` | 8000 (edge) | `/validate`, `/docs` | Validación de JWT para Traefik y agregación de la documentación OpenAPI |
| **auth** | `service_auth/` | 8001 | `/api/v1/users/login`, `/refresh` | Autenticación y emisión de JWT |
| **usuarios** | `service_usuarios/` | 8002 | `/api/v1/users`, `/doctors`, `/patients` | Usuarios, doctores, pacientes, recepcionistas, invitaciones, vinculación paciente–doctor |
| **pagos** | `service_pagos/` | 8003 | `/api/v1/subscriptions` | Suscripciones, checkout, portal de facturación, webhook y libro mayor de pagos |
| **transaccional** | `service_transaccional/` | 8004 | `/api/v1/chat` y `/api/v1/*` | Citas, consultas, expediente médico, bitácora, foros, chat y notificaciones |
| **shared_core** | `shared_core/` | — | — | `Base` ORM, cifrado, seguridad, enums, proveedores de llaves, utilidades de tiempo |

---

## 4. Cómo está construido cada servicio

Todos siguen la misma organización interna: **arquitectura hexagonal (puertos y adaptadores) aplicada por feature**. La regla de dependencia apunta siempre hacia adentro — la infraestructura conoce al dominio, nunca al revés.

```
service_pagos/
├── main.py            # App FastAPI: lifespan, routers, middleware
├── container.py       # Raíz de composición (dependency-injector)
├── Dockerfile · requirements.txt · tests/
└── app/
    └── subscriptions/                 # ── una carpeta por feature ──
        ├── domain/                    # Núcleo: entidades (Pydantic) + ports.py (Protocol).
        │                              #   No conoce FastAPI, ni SQLAlchemy, ni Stripe.
        ├── application/               # Casos de uso: una clase por archivo, un solo execute().
        │                              #   Depende solo de los ports y de dtos.py.
        └── infrastructure/            # Adaptadores concretos. Aquí vive la tecnología:
            ├── models/                #   ORM de SQLAlchemy
            ├── repositories/          #   Implementan los ports contra el ORM
            ├── adapters/              #   Servicios externos (Stripe) y estrategias
            ├── controllers/           #   schema ↔ entidad, errores → HTTPException
            ├── routes/                #   APIRouter delgados
            └── schemas/               #   Pydantic de petición y respuesta
```

Flujo de una petición: `routes/ → controllers/ → application/ → domain/ports.py`, con `infrastructure/repositories/` y `adapters/` implementando esos puertos.

El caso de uso solo conoce la interfaz declarada en `domain/ports.py`. Quién la implementa lo decide `container.py` al arrancar el servicio. Por eso las pruebas pueden sustituir cualquier puerto por un `MagicMock` sin tocar base de datos ni red.

### Features por servicio

| Servicio | Features (`app/<feature>/`) |
|---|---|
| `service_auth` | `auth` |
| `service_usuarios` | `users` (casos de uso agrupados en `doctor/`, `patient/`, `user/`, `invitation/`) |
| `service_pagos` | `subscriptions` |
| `service_transaccional` | `appointments`, `chat`, `consultations`, `forums`, `medical_record`, `notifications`, `patient_diaries`, `readmodels`, `core` |
| `service_gateway` | `jwt_validation`, `docs_aggregation` (usa `features/` en lugar de `app/`, por ser infraestructura sin dominio de negocio) |

### Base de datos

`shared_core.database` es completamente perezoso: nada se conecta al importar. `get_engine()` y `get_session_factory()` son fábricas cacheadas con `@lru_cache`. Cada `main.py` importa sus modelos en el *lifespan* y ejecuta `Base.metadata.create_all`. El `TimestampMixin` aporta `created_at` / `updated_at` con zona horaria de Ciudad de México.

---

## 5. Puesta en marcha

```bash
cp .env.example .env    # y llenar los valores
docker compose up --build
```

Levanta Traefik, Vault, PostgreSQL 16 y los cinco servicios. La API queda en `http://localhost:8000` y el Swagger agregado en `http://localhost:8000/docs`.

Pruebas (**148 en verde, 0 fallos**), desde el directorio de cada servicio:

```bash
cd service_pagos && ..\.venv\Scripts\python -m pytest
```

Detalle completo de requisitos, variables de entorno, desarrollo servicio por servicio y ejecución de pruebas: **[docs/puesta-en-marcha.md](docs/puesta-en-marcha.md)**.

---

## 6. Documentación

| Documento | Contenido |
|---|---|
| [Gateway](docs/gateway.md) | ForwardAuth, middlewares, roles, llaves en Vault |
| [Cifrado en reposo](docs/cifrado-en-reposo.md) | `EncryptedString`, Fernet, qué columnas están cifradas |
| [Métodos de pago](docs/metodos-de-pago.md) | Stripe, OXXO, SPEI, webhook idempotente |
| [Puesta en marcha](docs/puesta-en-marcha.md) | Requisitos, variables de entorno, pruebas |
| [ADRs](docs/adr.md) · [arquitectura](docs/arquitectura-microservicios.md) · [despliegue](docs/deploy-produccion-traefik-vault.md) | Decisiones, separación en servicios, Traefik + Vault en producción |
| [Requisitos](docs/project_requirements.md) · [trazabilidad](docs/traceability_matrix.md) · [diagramas](docs/diagramas) | Requisitos del proyecto y su seguimiento |

El resto de `docs/` cubre guías de integración para el frontend. [`CLAUDE.md`](CLAUDE.md) es la guía técnica de trabajo sobre el repositorio.
