# service_usuarios (:8002)

Servicio de **usuarios**. Dueño del CRUD de la tabla `users` y afines
(doctores, pacientes, recepcionistas, invitaciones).

- Se llena en la **Sesión 4** con `app/features/users` (sin el login → ese va a `service_auth`).
- Expone lecturas útiles (`GET /users/{id}`, `GET /patients/{id}`) para otros servicios.
- Rutas protegidas con `get_current_user` / `RoleChecker` de `shared_core` (claims del JWT).

Placeholder actual: solo `GET /health`.
