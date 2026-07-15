# Doctor & Receptionist Endpoints — Frontend Guide

Base URL: `/api/v1`

Todos los endpoints están bajo el router `doctors` (`prefix="/doctors"`). Ninguno requiere autenticación explícita actualmente (no hay `Depends(get_current_user)` en estas rutas) — verificar con backend si se requiere agregar guard antes de exponerlos en producción.

---

## 1. Detalles de un doctor

```
GET /api/v1/doctors/{doctor_id}
```

**200 OK**

```json
{
  "doctor_id": 12,
  "user_id": 34,
  "professional_license": "LIC-12345",
  "specialty": "Ginecología",
  "office": "Consultorio 4B",
  "name": "Ana",
  "last_name": "García",
  "email": "ana.garcia@example.com",
  "phone": "5512345678",
  "image_url": "https://.../avatar.jpg"
}
```

**404 Not Found** — si `doctor_id` no existe.

```json
{ "detail": "Doctor not found" }
```

---

## 2. Dashboard del doctor

```
GET /api/v1/doctors/{doctor_id}/dashboard
```

Pensado para la pantalla principal del doctor: sus recepcionistas (para poder mandarles mensaje por chat) y las citas de hoy.

**200 OK**

```json
{
  "receptionists": [
    {
      "user_id": 56,
      "name": "Laura",
      "last_name": "Pérez",
      "email": "laura.perez@example.com",
      "role": "recepcionista"
    }
  ],
  "today_appointments_count": 2,
  "today_appointments": [
    {
      "appointment_id": 101,
      "patient_id": 78,
      "patient_name": "María López",
      "appointment_time": "2026-07-08T15:30:00Z",
      "reason": "Control prenatal",
      "status": "pendiente"
    },
    {
      "appointment_id": 104,
      "patient_id": 79,
      "patient_name": "Sofía Ramírez",
      "appointment_time": "2026-07-08T17:00:00Z",
      "reason": null,
      "status": "confirmada"
    }
  ]
}
```

Notas:
- `receptionists[].user_id` es el id a usar para abrir el chat: `GET /api/v1/chat/history/{other_user_id}`.
- `today_appointments` viene ordenado por `appointment_time` ascendente.
- "Hoy" se calcula en horario de Ciudad de México (UTC-6 fijo), no en el timezone del navegador.
- `today_appointments_count` es simplemente `today_appointments.length` — ya viene calculado, no hace falta recalcularlo en el front.
- `status` viene en español, valores posibles: `pendiente`, `confirmada`, `cancelada`, `reprogramada`.

**404 Not Found** — si `doctor_id` no existe.

```json
{ "detail": "Doctor not found" }
```

---

## 3. Detalles de una recepcionista

```
GET /api/v1/doctors/receptionists/{receptionist_id}
```

**200 OK**

```json
{
  "receptionist_id": 7,
  "user_id": 56,
  "doctor_id": 12,
  "name": "Laura",
  "last_name": "Pérez",
  "email": "laura.perez@example.com",
  "phone": "5598765432",
  "image_url": null
}
```

**404 Not Found** — si `receptionist_id` no existe.

```json
{ "detail": "Receptionist not found" }
```

---

## 4. Dashboard de la recepcionista

```
GET /api/v1/doctors/receptionists/{receptionist_id}/dashboard
```

Pensado para la pantalla principal de la recepcionista: su nombre completo y las citas del doctor al que está asignada — **solo las que aún no han pasado**.

**200 OK**

```json
{
  "full_name": "Laura Pérez",
  "upcoming_appointments": [
    {
      "appointment_id": 101,
      "patient_id": 78,
      "patient_name": "María López",
      "appointment_time": "2026-07-09T15:30:00Z",
      "reason": "Control prenatal",
      "status": "pendiente"
    },
    {
      "appointment_id": 104,
      "patient_id": 79,
      "patient_name": "Sofía Ramírez",
      "appointment_time": "2026-07-10T17:00:00Z",
      "reason": null,
      "status": "confirmada"
    }
  ],
  "pending_appointments": [
    {
      "appointment_id": 101,
      "patient_id": 78,
      "patient_name": "María López",
      "appointment_time": "2026-07-09T15:30:00Z",
      "reason": "Control prenatal",
      "status": "pendiente"
    }
  ],
  "confirmed_appointments": [
    {
      "appointment_id": 104,
      "patient_id": 79,
      "patient_name": "Sofía Ramírez",
      "appointment_time": "2026-07-10T17:00:00Z",
      "reason": null,
      "status": "confirmada"
    }
  ]
}
```

Notas:
- `upcoming_appointments` = **todas** las citas futuras del doctor (cualquier status, incluye `cancelada`/`reprogramada` si las hay). Las citas ya pasadas nunca aparecen (se filtran en backend comparando contra la hora actual).
- `pending_appointments` y `confirmed_appointments` son subconjuntos de `upcoming_appointments` filtrados por `status == "pendiente"` / `"confirmada"` respectivamente — no hace falta filtrarlos de nuevo en el front.
- Las tres listas vienen ordenadas por `appointment_time` ascendente.
- `full_name` es el nombre completo de la recepcionista dueña del `receptionist_id` consultado (no del doctor).

**404 Not Found** — si `receptionist_id` no existe.

```json
{ "detail": "Receptionist not found" }
```

---

## Resumen de rutas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/doctors/{doctor_id}` | Detalles de un doctor |
| GET | `/doctors/{doctor_id}/dashboard` | Dashboard: recepcionistas + citas de hoy |
| GET | `/doctors/receptionists/{receptionist_id}` | Detalles de una recepcionista |
| GET | `/doctors/receptionists/{receptionist_id}/dashboard` | Dashboard: nombre + citas futuras (todas/pendientes/confirmadas) |
