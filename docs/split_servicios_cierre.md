# Split en 4 servicios — Cierre (Sesión 8)

Rama `split-servicios`. Monolito dividido por **vertical slicing** en 4 apps FastAPI
independientes sobre **una PostgreSQL compartida**, más el paquete común `shared_core`.

## Servicios

| Servicio | Puerto | Rutas | Responsabilidad |
|----------|--------|-------|-----------------|
| auth | 8001 | 1 | Login (`/api/v1/users/login`) + emisión de JWT con claims |
| usuarios | 8002 | 14 | CRUD usuarios, doctores, pacientes, recepcionistas, invitaciones |
| pagos | 8003 | 4 | Suscripciones y facturación (Stripe) |
| transaccional | 8004 | 34 | Citas, consultas, expediente, bitácora, foros, chat, notificaciones |

## Paridad de rutas — OK ✓

Unión de `openapi()["paths"]` de los 4 servicios = **53 rutas** = `EXPECTED_ROUTES`
del monolito (`tests/test_smoke.py`). **Cero faltantes, cero extra, cero solapes.**
Reproducible: `python scripts/route_parity_check.py`.

## Smoke e2e distribuido — 6/6 ✓

`scripts/smoke_distribuido.sh` (con los 4 servicios arriba y la misma `SECRET_KEY`):

1. Registrar doctor en **usuarios** → 201
2. Login en **auth** → 200, JWT emitido leyendo el doctor de la DB compartida
3. **pagos** `/subscriptions/me` con ese JWT → 200 (`pending`)
4. **transaccional** ruta gated con ese JWT → 200
5. Sin token → 401
6. Token firmado con otra `SECRET_KEY` → 401

Prueba **DB compartida** (una fila creada en usuarios es visible/usable en auth,
pagos y transaccional) y **contrato del token** (emitido por auth, validado local
por los otros 3 con la misma clave; rechazado si falta o si la firma no coincide).

## Decisiones de arquitectura aplicadas

- **DB compartida = contrato.** Cada servicio mapea solo las tablas que toca. Las
  tablas ajenas se leen con *read-models* propios (columnas mínimas), nunca
  importando el ORM de otro servicio ni por HTTP.
- **`ReadModelBase` separado.** Los read-models viven en `salud_prenatal_shared_core.
  database.ReadModelBase`, que `create_all` **nunca** toca. Así ningún servicio
  no-dueño crea una versión parcial de una tabla ajena (p. ej. `users` sin
  `password`) y **desaparece la carrera de `create_all`**: cada servicio crea solo
  sus tablas propias, disjuntas.
- **Auth por claims, sin DB.** `shared_core.auth_dependencies` arma un `Principal`
  desde los claims (`user_id`, `role`, `subscription_status`); `RoleChecker` y
  `require_active_subscription` leen claims, no repos.
- **Adapters cross-servicio reescritos** (transaccional): `patient_info`,
  `chat_user`, `chat_contacts`, `ad_eligibility`, `patient_cluster` y los lookups
  de citas leen la DB compartida vía read-models. Los puertos no cambian. El
  websocket de chat valida con `principal_from_token`.
- **`ad_eligibility` por lectura directa, no claim:** exige `plan_type == premium`,
  que el claim no transporta.
- **FKs externas stripeadas** en los modelos de transaccional (a `users`/`patients`/
  `doctors`): la integridad la define el servicio dueño del schema.

## Verificación por servicio (tests propios)

`auth 5 · usuarios 3 · pagos 6 · transaccional 5` = **19 tests en verde**.

## Notas / pendientes

- **`notifications`** quedó en transaccional (el plan de 8 features no la listaba
  entre las 6; es transversal transaccional).
- El **login conserva la respuesta rica** (auth lee varias tablas): no se tocó el
  frontend. El path `/api/v1/users/login` se mantuvo.
- **Sin retirar el monolito ni taggear** (requiere commits): `app/` y `main.py`
  raíz siguen como fuente en la rama. Antes de mergear `split-servicios`, taggear
  `pre-split` en `main`.
- **Opcional (demo docente):** convertir un lookup a HTTP real (p. ej.
  transaccional→pagos ad-eligibility) para mostrar comunicación de red, no solo DB.

## Cómo levantar

```
cp .env.example .env      # rellenar SECRET_KEY, ENCRYPTION_KEY (idénticas), DB_*, Stripe
docker compose up --build # postgres + auth:8001 usuarios:8002 pagos:8003 transaccional:8004
AUTH=http://localhost:8001 USUARIOS=http://localhost:8002 \
PAGOS=http://localhost:8003 TX=http://localhost:8004 ./scripts/smoke_distribuido.sh
```
