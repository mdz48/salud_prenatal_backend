# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Microservices backend for a prenatal health platform (salud_prenatal_backend). FastAPI per service, a **single shared PostgreSQL** via SQLAlchemy, JWT auth, DI via `dependency-injector`. A sibling project, `machine_learning_service`, serves preeclampsia-risk predictions consumed over HTTP.

> **The `app/` monolith at the repo root is DEAD — not used for anything.** Root `main.py`, root `tests/`, and everything under `app/features/**` / `app/core/**` are the retired pre-migration monolith. **Never read or edit them to understand or change current behavior.** All live code lives in `service_*/` and `shared_core/`. (Git may still show uncommitted churn under `app/` — ignore it.)

## Services

Five FastAPI services + one shared package, all built from the repo root (`context: .`, each with its own `service_*/Dockerfile`). Each service dir has its own `app/`, `container.py`, `main.py`, `requirements.txt`, and `tests/`.

| Service | Port | Path prefix(es) | Responsibility |
|---|---|---|---|
| `service_gateway` | 8000 | edge | Traefik ForwardAuth target (`/validate`, `/validate/strict`) + docs aggregation. `features/` layout (not `app/`). |
| `service_auth` | 8001 | `/api/v1/users/login`, `/refresh` | Issues JWTs (login/refresh). |
| `service_usuarios` | 8002 | `/api/v1/users`, `/doctors`, `/patients` | Users, doctors, patients. |
| `service_pagos` | 8003 | `/api/v1/subscriptions` | Stripe: checkout (recurring + one-time OXXO/SPEI), billing portal, webhook + payment ledger. |
| `service_transaccional` | 8004 | `/api/v1/chat`, else `/api/v1/*` | appointments, chat, consultations, forums, medical_record, notifications, patient_diaries, readmodels. |
| `shared_core` | — | — | Installable pkg `salud_prenatal_shared_core`: `Base`, enums, `auth_dependencies`, `database`, `security`, `crypto`, `time`, `events`, Vault JWT key providers. |

Infra (in `docker-compose.yml`): **Traefik** v3.7 edge router, **Vault** (JWT signing keys), one **Postgres 16** (`DB_NAME` `salud_prenatal`, shared by all services).

## Commands

All Python runs through the local venv — never invoke global `pip`/`python`.

```bash
docker compose up --build                                    # all services + postgres + traefik + vault
.venv\Scripts\pip install -r service_pagos/requirements.txt  # install a service's deps
cd service_pagos && uvicorn main:app --reload --port 8003    # run ONE service in dev
cd service_pagos && ..\.venv\Scripts\python -m pytest        # test ONE service
pip install -e ./shared_core                                 # shared_core as editable pkg
```

Run/test **per service** — pick the service dir first. There is no repo-wide server or test entrypoint anymore (the root `main.py`/`tests/` belong to the dead monolith).

### Dependency Management (from AGENTS.md — must follow)

- Any new import/library MUST be added to the **owning service's** `requirements.txt` before finishing a task (or `shared_core/requirements.txt` if it belongs there).
- Never install packages globally — always target `.venv`.
- After adding to a `requirements.txt`, remind the user to reinstall it.

## Architecture

### Hexagonal / Clean Architecture per feature (inside each service)

Within a service, every feature under `app/<feature>/` follows this layout:

- `domain/` — entities (Pydantic, no ORM imports) and `ports.py` (`Protocol` interfaces the use cases depend on).
- `application/` — one use case class per file (e.g. `create_checkout_session_usecase.py`), each a single `execute(...)`. Depends only on domain ports + application DTOs (`application/dtos.py`), never on infrastructure. Controllers map schema → DTO.
- `infrastructure/` — concrete adapters: `models/` (SQLAlchemy ORM), `repositories/` (implement ports against the ORM), `controllers/` (schema ↔ entity/DTO, catch exceptions → `HTTPException`), `routes/` (thin `APIRouter`), `schemas/` (Pydantic req/resp), `adapters/` for external services (Stripe, ML) or strategy variants (e.g. `stripe_checkout_strategies.py`: recurring vs one-time).

### Service boundaries

- **The shared DB is the contract.** Each service defines its OWN ORM models for the tables it touches. A service never imports another service's code.
- **Cross-service communication:** primarily the shared DB; a few explicit HTTP hops exist (e.g. `service_usuarios` → `service_transaccional` via `TRANSACCIONAL_URL`, and the gateway's ForwardAuth). External integrations (ML, Stripe) are always HTTP.

### Auth & authorization (edge-validated, header-propagated)

- **Traefik** applies a `jwt-auth`/`jwt-strict` ForwardAuth middleware → **`service_gateway`** `/validate`. The gateway decodes the JWT (`principal_from_token`, signing keys from **Vault** via `get_jwt_key_provider`) and injects `X-User-Id / X-User-Email / X-User-Role / X-Subscription-Status / X-Subscription-Period-End` headers.
- **Downstream services do NOT decode JWTs and do NOT hit the DB for identity.** They call `principal_from_headers(request.headers)` → `Principal` from `shared_core.auth_dependencies`. Malformed headers degrade field-by-field to `None`, never raise.
- `RoleChecker([RoleEnum...])` (in `shared_core.auth_dependencies`) gates routes on the `Principal`'s role — e.g. `require_doctor = RoleChecker([RoleEnum.doctor])`.
- `shared_core.security.get_secret_key()` raises if `SECRET_KEY` is unset — never add a hardcoded fallback (it would let anyone forge JWTs).

### Dependency Injection

Each service has its OWN composition root in `service_*/container.py` (`dependency_injector`), wiring repositories → adapters → use cases → controllers as `providers.Factory`. Routers resolve controllers from that container. When adding a use case/repository/adapter, register it in that service's `container.py`.

### Database

`shared_core.database` is fully lazy — nothing connects at import time. `get_engine()`/`get_session_factory()` are `@lru_cache` factories; `DATABASE_URL` overrides everything (tests use SQLite), otherwise built from `DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT`/`DB_NAME`. `TimestampMixin` (uses `shared_core.time.now_cdmx`) provides `created_at`/`updated_at`. Each service's `main.py` lifespan imports its models then runs `Base.metadata.create_all` (no Alembic — schema changes go into the ORM models). `db_cleanup.close_db_after(Container)` decorates routes to close the request session.

### Partial updates

Update endpoints pass `schema.model_dump(exclude_unset=True)` as a plain dict to `repository.update(id, changes)`, which does selective `setattr` with an immutable-keys blacklist. Never construct domain entities with dummy IDs to represent partial updates.

### Crypto

`shared_core.crypto` holds field-level encryption (`ENCRYPTION_KEY`, Fernet) for `EncryptedString` columns; keys are lazy via `@lru_cache`.

### Webhooks & idempotency (service_pagos)

Stripe webhooks are idempotent via a payment-transaction ledger: `HandlePaymentEventUseCase` checks `exists_by_event_id` before applying, so retried `one_time_payment_succeeded` events don't double-add +30 days. `GET /subscriptions/me` exposes `auto_renewal` (= has a Stripe subscription) — the discriminator clients use to choose portal (recurring) vs new checkout (one-time OXXO/SPEI).

### Tests

Per-service `tests/` mirror feature names (`tests/test_<feature>/`) and mock ports with `MagicMock`. Integration tests are marked `@pytest.mark.integration` and run the real service app against SQLite (set env like `DATABASE_URL`/`SECRET_KEY`/`ENCRYPTION_KEY` before importing `main` — keep env-dependent config lazy). Run tests from inside the target service dir.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- graphify indexes the whole repo including the dead `app/` monolith — prefer results under `service_*/` and `shared_core/`, and ignore hits under `app/`.
