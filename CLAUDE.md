# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for a prenatal health platform (salud_prenatal_backend). PostgreSQL via SQLAlchemy, JWT auth, DI via `dependency-injector`. A separate sibling project, `machine_learning_service` (also mounted as a working directory), serves preeclampsia-risk predictions consumed over HTTP by this backend.

## Commands

All commands run through the local venv — never invoke global `pip`/`python`.

```
.venv\Scripts\pip install -r requirements.txt      # install deps
.venv\Scripts\python main.py                        # not typical entrypoint; use uvicorn instead
.venv\Scripts\python -m uvicorn main:app --reload    # run dev server (http://localhost:8000)
.venv\Scripts\python -m pytest                       # run full test suite
.venv\Scripts\python -m pytest tests/test_medical_record/test_create_medical_record_usecase.py  # single file
.venv\Scripts\python -m pytest tests/test_medical_record -k create                                # by keyword
.venv\Scripts\python scripts/apply_indexes.py        # apply DB indexes (see script for what it manages)
```

Docker: `Dockerfile` builds a slim image running `uvicorn main:app --host 0.0.0.0 --port 8000`; see [docs/docker_doc.md](docs/docker_doc.md) for details.

### Dependency Management (from AGENTS.md — must follow)

- Any new import/library MUST be added to `requirements.txt` before finishing a task.
- Never install packages globally — always target `.venv` (`.venv\Scripts\pip install <package>`).
- After adding to `requirements.txt`, remind the user to run `.venv\Scripts\pip install -r requirements.txt`.

## Architecture

### Hexagonal / Clean Architecture per feature

Each feature under `app/features/<feature>/` is being migrated to this layout:

- `domain/` — entities (plain dataclass-like objects, no ORM) and `ports.py` (`Protocol` interfaces for repositories/external services the use cases depend on).
- `application/` — one use case class per file (e.g. `create_medical_record_usecase.py`), each with a single `execute(...)` method. Depends only on domain ports, never on infrastructure directly.
- `infrastructure/` — concrete adapters: `models/` (SQLAlchemy ORM models), `repositories/` (implement the domain ports against the ORM), `controllers/` (translate HTTP schemas ↔ domain entities, catch exceptions and raise `HTTPException`), `routes/` (FastAPI `APIRouter`, thin — just wires request → controller method), `schemas/` (Pydantic request/response models), and feature-specific `adapters/` for external services (e.g. `medical_record/infrastructure/adapters/ml_prediction_adapter.py` calls the ML microservice over HTTP).

**Important:** several features (`appointments`, `medical_record`, etc.) still have legacy flat directories (`models/`, `repositories/`, `routes/`, `schemas/`, `services/`) left over from before the hexagonal migration. `main.py` and `app/core/containers.py` only wire up the `infrastructure/`+`application/`+`domain/` versions — the legacy sibling files are dead code not imported anywhere. When editing a feature, always confirm which version is actually wired in `containers.py`/`main.py` before touching a file; don't assume the flat-layout file is live.

Features not yet needing a `models`/legacy split (e.g. `chat`, `forums`) only have the new three-layer structure.

### Dependency Injection

`app/core/containers.py` is the single composition root (`dependency_injector.containers.DeclarativeContainer`). It wires: DB session (`providers.Resource(get_db)`) → repositories → use cases → controllers, all as `providers.Factory`. Routers pull controllers via `@inject` + `Depends(Provide[Container.<controller_name>])`. When adding a new use case or repository, register it here and add its module to `wiring_config.modules` if it uses `@inject`.

### Auth & authorization

- `app/core/dependencies.py`: `get_current_user` decodes the JWT (via `app/core/security.py`'s `SECRET_KEY`/`ALGORITHM`) and loads the user directly through `UserRepository` (bypasses the DI container intentionally, since it's a raw `Depends`, not injected via container).
- `RoleChecker([RoleEnum...])` is a reusable dependency factory for role-gating routes (see `require_doctor = RoleChecker([RoleEnum.doctor])` pattern in routers).

### Database

`app/core/database.py` builds the Postgres URL from env vars (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`); on connection failure it falls back to `LOCAL_URL` for local dev. `TimestampMixin` (uses `app/core/time.py`'s `now_cdmx` for CDMX-local timestamps) provides `created_at`/`updated_at` for models that include it. Tables are created via `Base.metadata.create_all(bind=engine)` at the bottom of `main.py` (no Alembic migrations in use — schema changes go straight into SQLAlchemy models).

### Crypto

`app/core/crypto/` holds `crypto_pipes.py` and `key_manager.py` for field-level encryption; covered by `tests/test_crypto_pipes.py` and `tests/test_key_manager.py`.

### Cross-feature calls

Some use cases reach across feature boundaries directly against another feature's repository (e.g. `medical_record`'s use cases take a `patient_repository` from `users`, `authenticate_user_usecase` pulls in `patient_repository`/`doctor_repository`/`receptionist_repository`/`medical_record_repository`). There's no anti-corruption layer between features — ports typically type cross-feature dependencies loosely (e.g. `IPatientRepository.get_by_id` returns `Optional[object]`) rather than importing the other feature's entity.

### Tests

Tests under `tests/` mirror feature names (`tests/test_<feature>/test_<feature>_usecases.py`) and mostly unit-test use cases with mocked repositories/ports — no live DB required for most tests. `tests/test_integration_endpoints.py` is the exception (hits actual routes/DB). Run a feature's tests directory or a single test function with `-k` as shown above.
