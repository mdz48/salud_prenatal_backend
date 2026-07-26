# Resumen — División del monolito en 4 servicios

Rama `split-servicios`. El monolito FastAPI (`salud_prenatal_backend`) se dividió
por **vertical slicing** en **4 apps desplegables** sobre **una PostgreSQL
compartida**, más el paquete común `shared_core`. Todo escrito en la rama, **sin
commits** (los hace/pushea el usuario).

## Qué se hizo, sesión por sesión

| Sesión | Entregable | Estado |
|--------|-----------|--------|
| 4 | `service_usuarios` (:8002) — CRUD, read-models de dashboards, sin login | ✓ 3 tests |
| 5 | `service_auth` (:8001) — login + emisión de JWT con claims | ✓ 5 tests |
| 6 | `service_transaccional` (:8004) — 7 features, adapters cross-servicio reescritos | ✓ 5 tests |
| 7 | Orquestación — 4 Dockerfiles + `docker-compose.yml` (postgres + 4 servicios) | ✓ compose válido |
| 8 | Verificación — paridad de rutas + smoke e2e distribuido + reporte | ✓ paridad OK, 6/6 |

## Los 4 servicios

| Servicio | Puerto | Rutas | Responsabilidad |
|----------|--------|-------|-----------------|
| auth | 8001 | 1 | Login (`/api/v1/users/login`) + JWT |
| usuarios | 8002 | 14 | Usuarios, doctores, pacientes, recepcionistas, invitaciones |
| pagos | 8003 | 4 | Suscripciones (Stripe) |
| transaccional | 8004 | 34 | Citas, consultas, expediente, bitácora, foros, chat, notificaciones |

## Verificación final

- **Tests por servicio:** auth 5 · usuarios 3 · pagos 6 · transaccional 5 = **19 en verde**.
- **Paridad de rutas:** unión de los 4 servicios = **53 rutas = las 53 del monolito**
  (`EXPECTED_ROUTES`), sin faltantes, extra ni solapes. → `scripts/route_parity_check.py`.
- **Smoke e2e distribuido (6/6):** doctor en usuarios → login en auth → mismo JWT
  aceptado por pagos (`pending`) y transaccional; 401 sin token y con firma inválida.
  Prueba DB compartida + contrato del token. → `scripts/smoke_distribuido.sh`.

## Decisiones de arquitectura clave

- **DB compartida = contrato.** Cada servicio mapea solo sus tablas; las ajenas se
  leen con *read-models* propios (columnas mínimas), sin importar ORM de otro
  servicio ni HTTP.
- **`ReadModelBase` separado** (hallazgo importante): los read-models viven en una
  Base que `create_all` nunca toca, así ningún servicio no-dueño crea una tabla
  ajena **parcial** (p. ej. `users` sin `password`). Esto además **eliminó la
  carrera de `create_all`** que el plan marcaba como riesgo: cada servicio crea
  solo sus tablas, disjuntas.
- **Auth por claims, sin DB:** `Principal` desde el JWT; `RoleChecker` y la
  verificación de suscripción leen claims, no repos.
- **Adapters cross-servicio de transaccional reescritos** a read-models sin cambiar
  sus puertos (patient_info, chat_user, chat_contacts, ad_eligibility,
  patient_cluster, lookups de citas). Websocket de chat → `principal_from_token`.
- **`ad_eligibility` lee la tabla** (no claim): necesita `plan_type`, que el token
  no transporta.
- **Login conserva la respuesta rica** → no se tocó el frontend; se mantuvo el path.

## Pendientes (requieren commits)

- Borrar el `.git/index.lock` colgado, luego commit + push de la rama.
- Retirar el monolito (`app/`, `main.py`) y taggear `pre-split` en `main` antes de mergear.
- Opcional (demo docente): convertir un lookup a HTTP real (transaccional→pagos)
  para mostrar comunicación de red, no solo DB compartida.

## Cómo levantar

```
cp .env.example .env      # SECRET_KEY y ENCRYPTION_KEY idénticas en los 4; DB_*; Stripe
docker compose up --build # postgres + auth:8001 usuarios:8002 pagos:8003 transaccional:8004
AUTH=http://localhost:8001 USUARIOS=http://localhost:8002 \
PAGOS=http://localhost:8003 TX=http://localhost:8004 ./scripts/smoke_distribuido.sh
```
