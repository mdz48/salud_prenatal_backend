# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for a prenatal health platform (salud_prenatal_backend). PostgreSQL via SQLAlchemy, JWT auth, DI via `dependency-injector`. A separate sibling project, `machine_learning_service` (also mounted as a working directory), serves preeclampsia-risk predictions consumed over HTTP by this backend.

## Commands

All commands run through the local venv — never invoke global `pip`/`python`.

```
.venv\Scripts\pip install -r requirements.txt      # install deps
.venv\Scripts\python -m uvicorn main:app --reload    # run dev server (http://localhost:8000)
.venv\Scripts\python -m pytest                       # run full test suite
.venv\Scripts\python -m pytest tests/test_medical_record/test_create_medical_record_usecase.py  # single file
.venv\Scripts\python -m pytest tests/test_medical_record -k create                                # by keyword
.venv\Scripts\python -m pytest -m integration        # only integration tests (app + SQLite)
.venv\Scripts\python scripts/apply_indexes.py        # apply DB indexes (see script for what it manages)
```

Docker: `Dockerfile` builds a slim image running `uvicorn main:app --host 0.0.0.0 --port 8000`; see [docs/docker_doc.md](docs/docker_doc.md) for details.

### Dependency Management (from AGENTS.md — must follow)

- Any new import/library MUST be added to `requirements.txt` before finishing a task.
- Never install packages globally — always target `.venv` (`.venv\Scripts\pip install <package>`).
- After adding to `requirements.txt`, remind the user to run `.venv\Scripts\pip install -r requirements.txt`.

## Architecture

### Hexagonal / Clean Architecture per feature

Every feature under `app/features/<feature>/` follows this layout (legacy flat directories were removed in the clean-architecture migration — if you see a `models/` or `services/` directly under a feature, it shouldn't exist):

- `domain/` — entities (Pydantic models, no ORM imports) and `ports.py` (`Protocol` interfaces for repositories/external services the use cases depend on).
- `application/` — one use case class per file (e.g. `create_medical_record_usecase.py`), each with a single `execute(...)` method. Depends only on domain ports and application DTOs, never on infrastructure. Where use cases need input shapes, they take plain dataclass DTOs from `application/dtos.py` (see `users`); controllers map Pydantic schema → DTO.
- `infrastructure/` — concrete adapters: `models/` (SQLAlchemy ORM), `repositories/` (implement domain ports against the ORM), `controllers/` (schema ↔ entity/DTO mapping, catch exceptions → `HTTPException`), `routes/` (thin FastAPI `APIRouter`), `schemas/` (Pydantic request/response), and `adapters/` for external services or cross-feature access.

### Cross-feature access pattern (ports propios + adapters)

A feature never imports another feature's repositories or ORM models. Instead, the consuming feature defines its OWN port in its `domain/ports.py`, typed with its own DTO, and an adapter in its `infrastructure/adapters/` wraps the other feature's repository:

- `medical_record` → `users`: `IPatientInfoPort` + `PatientInfo` DTO ([ports.py](app/features/medical_record/domain/ports.py)), implemented by `PatientInfoAdapter` (resolves `patient.user` lazy-load inside the request's live session).
- `users` → `appointments`/`medical_record`: `IAppointmentLookup` / `IMedicalRecordLookup` in users' ports, implemented by thin adapters in `users/infrastructure/adapters/`.

Routers may import another feature's **domain entity** (e.g. `UserEntity` for the `get_current_user` dependency) but never its ORM model.

Accepted pragmatic exceptions (documented decision — do not "fix"): `patient_entity` nests `UserEntity`, and `medical_record_entity` nests consultation/diary entities.

### Dependency Injection

`app/core/containers.py` is the single composition root (`dependency_injector.containers.DeclarativeContainer`). It wires: DB session (`providers.Resource(get_db)`) → repositories → adapters → use cases → controllers, all as `providers.Factory`. Wiring is declared ONCE in `Container.wiring_config` (includes `app.core.dependencies` and every router module) — do not add a second `container.wire(...)` call elsewhere. `main.py`'s lifespan only runs `Base.metadata.create_all(bind=get_engine())` on startup. When adding a use case/repository/adapter, register it here and add its module to `wiring_config.modules` if it uses `@inject`.

### Auth & authorization

- `app/core/dependencies.py`: `get_current_user` decodes the JWT and gets its `IUserRepository` via the container (`@inject` + `Provide[Container.user_repository]`) — tests can override with `app.container.user_repository.override(...)`.
- `app/core/security.py`: `get_secret_key()` raises `RuntimeError` if `SECRET_KEY` is unset (never add a hardcoded fallback — that lets anyone forge JWTs). Crypto pipes for `EncryptedString` are lazy via `@lru_cache`.
- `RoleChecker([RoleEnum...])` is a reusable dependency factory for role-gating routes (see `require_doctor = RoleChecker([RoleEnum.doctor])` pattern in routers).

### Database

`app/core/database.py` is fully lazy — nothing connects at import time. `get_engine()`/`get_session_factory()` are `@lru_cache` factories; `DATABASE_URL` env var overrides everything (tests use SQLite through it), otherwise the URL is built from `DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT`/`DB_NAME` with fallback to `LOCAL_URL` on connection failure. `TimestampMixin` (uses `app/core/time.py`'s `now_cdmx`) provides `created_at`/`updated_at`. Schema is created via `create_all` in `main.py`'s lifespan (no Alembic — schema changes go straight into SQLAlchemy models).

### Partial updates

Update endpoints pass `schema.model_dump(exclude_unset=True)` as a plain dict down to `repository.update(id, changes)`, which does selective `setattr` with an immutable-keys blacklist (see `medical_record_repository.update`). Never construct domain entities with dummy IDs to represent partial updates.

### Crypto

`app/core/crypto/` holds `crypto_pipes.py` and `key_manager.py` for field-level encryption (`ENCRYPTION_KEY` env var, Fernet); covered by `tests/test_crypto_pipes.py` and `tests/test_key_manager.py`.

### Tests

`tests/conftest.py` sets test env (SQLite via `DATABASE_URL`, `SECRET_KEY`, `ENCRYPTION_KEY`) BEFORE importing `main` — keep any new env-dependent config lazy so this keeps working. Unit tests mirror feature names (`tests/test_<feature>/`) and mock ports with `MagicMock`. Integration tests are marked `@pytest.mark.integration` (registered in `pytest.ini`) and run the real app against SQLite: `test_smoke.py` guards `/health` plus a **route snapshot** (`app.openapi()["paths"]` — the public API surface must not change unintentionally; update `EXPECTED_ROUTES` deliberately when adding endpoints), and `test_medical_record_e2e.py` exercises the cross-feature `PatientInfoAdapter` end to end.
