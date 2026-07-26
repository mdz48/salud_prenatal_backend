# service_auth (:8001)

Servicio de **autenticación**. Delgado: verifica credenciales sobre la tabla `users`
(DB compartida) y emite el JWT con claims `user_id`, `role`, `subscription_status`.

- **Emite** tokens; los demás servicios solo los **validan** localmente (misma `SECRET_KEY`).
- Se llena en la **Sesión 5** moviendo `AuthenticateUserUseCase` + `auth_controller` + ruta `POST /login`.
- No es dueño de la tabla `users` (eso es de `usuarios`); solo la lee para el login.

Placeholder actual: solo `GET /health`.
