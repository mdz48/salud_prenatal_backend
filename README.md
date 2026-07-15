# Salud Prenatal — Monorepo de servicios

Monorepo con **4 servicios FastAPI independientes** sobre una **PostgreSQL compartida**, más un paquete común `shared_core`. Resultado de dividir el monolito original (`app/`, `main.py`) por vertical slicing.

> Rama de trabajo: `split-servicios`. El monolito original sigue funcionando en `main`/`develop` hasta lograr paridad.

## Servicios

| Servicio | Carpeta | Puerto | Responsabilidad |
|----------|---------|--------|-----------------|
| **auth** | `service_auth/` | 8001 | Login, emisión y validación de JWT |
| **usuarios** | `service_usuarios/` | 8002 | CRUD de usuarios, doctores, pacientes, recepcionistas, invitaciones |
| **pagos** | `service_pagos/` | 8003 | Suscripciones y facturación (Stripe) |
| **transaccional** | `service_transaccional/` | 8004 | Citas, consultas, expediente médico, bitácora, foros, chat, notificaciones |
| _(común)_ | `shared_core/` | — | `Base`/ORM mixins, seguridad JWT, cripto, enums, tiempo |

## Arquitectura (resumen)

```
                 ┌──────────────────────────────────────┐
                 │        PostgreSQL (compartida)        │
                 └──────────────────────────────────────┘
                    ▲        ▲          ▲          ▲
                    │        │          │          │
              ┌─────┴──┐ ┌───┴────┐ ┌───┴───┐ ┌────┴────────┐
              │ auth   │ │usuarios│ │ pagos │ │transaccional│
              │ :8001  │ │ :8002  │ │ :8003 │ │   :8004     │
              └────────┘ └────────┘ └───────┘ └─────────────┘
                    │
      auth emite JWT ─ el resto valida local con SECRET_KEY (claims: user_id, role, subscription_status)
```

Principios:
- **La DB compartida es el contrato.** Cada servicio define sus propios modelos ORM para las tablas que toca. Ningún servicio importa código de otro servicio.
- **Comunicación entre servicios:** JWT (emitido por auth) + lectura directa a la DB compartida. Sin llamadas HTTP internas (salvo integraciones externas: ML y Stripe).
- **`shared_core`** provee lo común (`Base`, `EncryptedString`, seguridad, cripto) como paquete instalable (`pip install -e ./shared_core`).

## Cómo levantar (cuando esté completo)

```bash
docker compose up --build      # los 4 servicios + postgres
```

Cada servicio individual (desarrollo):
```bash
cd service_auth
uvicorn main:app --reload --port 8001
```

## Estado

Scaffold inicial (Sesión 0). Los servicios se llenan con código real en sesiones sucesivas — ver el plan de migración.
