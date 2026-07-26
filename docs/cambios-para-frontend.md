# Cambios del backend (monolito → servicios) — Guía para el Frontend

> El backend monolito se dividió en 4 servicios detrás de un **API Gateway**. Este
> documento resume **qué cambió y qué NO** desde el punto de vista del frontend, para
> que sepas exactamente qué revisar. Fecha del corte: julio 2026.

---

## TL;DR

- **La URL base NO cambió.** Todo sigue en `https://saludprenatal.sytes.net`. El frontend le pega al mismo dominio; ahora detrás hay un gateway que enruta a los servicios.
- **Las rutas NO cambiaron.** Los 53 endpoints `/api/v1/...` son **idénticos** en path y método (verificado 1:1 contra el monolito).
- **El contrato de request/response NO cambió.** Mismos bodies, mismos campos.
- **Hubo UN bug de comportamiento que rompía rutas en el navegador → ya está corregido** (ver §2). Si el frontend fallaba en listados, era esto.
- **Novedad menor en el token:** el JWT ahora incluye un claim `subscription_status` (además de los que ya tenía). No rompe nada; es aditivo.

---

## 1. Lo que NO cambió (puedes confiar en esto)

- **Dominio y esquema:** `https://saludprenatal.sytes.net/api/v1/...` igual que antes.
- **Login:** `POST /api/v1/users/login` — mismo path, mismo body (`{email, password}` o form `username/password`), **misma respuesta** (`access_token`, `token_type`, `user_id`, `role`, `patient_id`, `doctor_id`, `medical_record_id`, `receptionist_id`, `receptionist`, `subscription_status`).
- **Todos los paths y métodos:** appointments, chat, consultations, doctors, forums, medical-records, notifications, patient-diaries, patients, subscriptions, users → **iguales**.
- **Autenticación:** mismo header `Authorization: Bearer <jwt>`. Los tokens viejos siguen siendo válidos hasta expirar.
- **WebSocket de chat:** `wss://saludprenatal.sytes.net/api/v1/chat/ws?token=<jwt>` — igual.

---

## 2. El bug que rompía rutas (YA CORREGIDO)

**Síntoma:** algunas rutas "dejaron de servir" en el frontend (típicamente **listados**: `GET /api/v1/users`, `/api/v1/appointments`, `/api/v1/consultations`, etc.).

**Causa:** esas rutas de colección, cuando se llaman **sin `/` final**, responden un redirect `307` hacia la versión con `/`. El gateway estaba devolviendo ese redirect apuntando al **host interno de Docker** (`http://usuarios:8002/...`), que el navegador no puede alcanzar → la petición fallaba. (En el monolito el redirect quedaba en el mismo dominio, por eso antes funcionaba.)

**Corrección aplicada:** el gateway ahora reescribe el redirect a una ruta **relativa** (`/api/v1/users/`), que el navegador resuelve contra el dominio público. **Ya funciona.**

**Recomendación (opcional, buena práctica):** para los endpoints de colección, llama directo a la versión **con `/` final** y te ahorras el salto de redirect:
- `GET /api/v1/users/`  ✅ (en vez de `/api/v1/users`)
- `GET /api/v1/appointments/`  ✅
- `GET /api/v1/consultations/`  ✅
- `POST /api/v1/patients/register`, `POST /api/v1/doctors/register` → no tienen slash final, no aplica.

> Si el frontend ya usa las rutas exactas de la documentación (con su slash tal cual), no hay nada que cambiar. El fix del gateway cubre ambos casos.

---

## 3. Novedad en el token (aditiva, no rompe nada)

El JWT que emite el login ahora incluye estos claims:

```
sub                 = email
user_id             = id
role                = doctor | paciente | recepcionista | admin
subscription_status = active | pending | past_due | canceled | null   <-- NUEVO
exp                 = expiración
```

- `subscription_status` se agregó para que los servicios validen la suscripción **sin consultar la base de datos** en cada request.
- El frontend **no necesita hacer nada**: si ya leías `subscription_status` del **body** de la respuesta de login, sigue estando ahí igual. Ahora además viaja dentro del token.

---

## 4. Punto de entrada (sin cambios para ti, contexto útil)

```
Frontend  ─HTTPS/WSS→  saludprenatal.sytes.net (Traefik)
                        │   └── por cada request le pregunta al API Gateway
                        │       si el token es válido (y quién eres)
                        │
                        ├─ /api/v1/users/login|refresh   → servicio auth
                        ├─ /api/v1/users|doctors|patients → servicio usuarios
                        ├─ /api/v1/subscriptions/*        → servicio pagos
                        └─ /api/v1/* (resto) + chat ws    → servicio transaccional
```

- El token se valida **una sola vez** en la entrada. **Tú le pegas solo al dominio, como siempre.**
- **Cambio de comportamiento a tener en cuenta:** un token inválido o expirado ahora se
  rechaza con `401` en la entrada, antes de llegar al servicio. En el **WebSocket** eso
  significa que el *handshake falla* (el connect no se abre) en vez de conectar y cerrarse
  al instante. Si tu código ya maneja el error de conexión del WS, no hay nada que hacer.
- **Swagger** para explorar: `https://saludprenatal.sytes.net/docs` (selector arriba a la derecha para elegir servicio: Usuarios / Pagos / Transaccional / Auth).

---

## 5. Checklist para el frontend

- [ ] Si algún listado fallaba, **volver a probar**: el fix del redirect ya está en producción.
- [ ] (Opcional) Asegurar que los listados usen la ruta **con `/` final** para evitar el salto de redirect.
- [ ] Confirmar que el flujo de login sigue guardando el `access_token` igual (sin cambios).
- [ ] Nada más: paths, métodos, bodies y auth son idénticos.

---

## 6. Cómo verificar rápido (curl)

```bash
D=https://saludprenatal.sytes.net

# login
TOKEN=$(curl -s -X POST $D/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"...","password":"..."}' | jq -r .access_token)

# listado con slash (recomendado)
curl -s $D/api/v1/users/ -H "Authorization: Bearer $TOKEN"

# listado sin slash (ahora también funciona, hace 1 redirect)
curl -sL $D/api/v1/users -H "Authorization: Bearer $TOKEN"
```

---

## Resumen de una línea

**Para el frontend, la API es la misma que el monolito** (mismo dominio, rutas, métodos y bodies). El único problema real era el redirect de los listados sin `/` final, **ya corregido en el gateway**. Lo único nuevo es un claim `subscription_status` dentro del token, que no requiere cambios.
