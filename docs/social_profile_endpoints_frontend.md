# Perfil Social — Frontend Guide

Base URL: `/api/v1`

Todos los endpoints están bajo el router `forums` (`prefix="/forums"`). Aplica tanto a **pacientes** como a **doctores** — cualquier usuario autenticado tiene un solo perfil social, identificado por su `user_id`.

Los tres endpoints de creación y edición requieren `Authorization: Bearer <token>`. Sin token → `401`.

---

## 1. Crear mi perfil

```
POST /api/v1/forums/profiles
```

Se usa una sola vez, la primera vez que el usuario configura su perfil social. El `user_id` **no se envía** — se toma del token.

**Body**

```json
{
  "alias": "maria_lopez",
  "bio": "Embarazada de 24 semanas, primer bebé",
  "avatar_url": "https://cdn.example.com/avatar.png",
  "office_address": "Consultorio 4B, Hospital Central"
}
```

Todos los campos son opcionales (`Optional[str] = None`). `office_address` normalmente solo lo llenan doctores, pero el backend no lo restringe por rol.

**201 Created**

```json
{
  "user_id": 3,
  "alias": "maria_lopez",
  "bio": "Embarazada de 24 semanas, primer bebé",
  "avatar_url": "https://cdn.example.com/avatar.png",
  "office_address": null
}
```

Nota: `cluster_profile` **no se expone** en la respuesta — es un dato derivado del modelo de ML a partir de información médica, nunca lo envía ni lo ve el cliente.

---

## 2. Editar mi perfil

```
PATCH /api/v1/forums/profiles/me
```

**Nuevo.** Edita el perfil del usuario autenticado — no existe (ni existirá) una variante con `{user_id}` en el path: un usuario **solo puede editar su propio perfil**, nunca el de otro (`user_id` siempre sale del token, jamás del cliente).

Es un update **parcial**: mandá solo los campos que querés cambiar. Cualquier campo omitido en el body queda intacto en el backend (no lo pises con `null` a propósito — si un campo no viene en el JSON, no se toca; si viene explícitamente como `null`, sí se borra).

**Body** (todos los campos opcionales — mandá solo lo que cambia)

```json
{
  "bio": "Nueva bio",
  "avatar_url": "https://cdn.example.com/nuevo-avatar.png"
}
```

**200 OK** — perfil completo actualizado

```json
{
  "user_id": 3,
  "alias": "maria_lopez",
  "bio": "Nueva bio",
  "avatar_url": "https://cdn.example.com/nuevo-avatar.png",
  "office_address": null
}
```

**404 Not Found** — el usuario todavía no tiene perfil creado (llamar primero a `POST /forums/profiles`)

```json
{ "detail": "Profile not found" }
```

**409 Conflict** — el `alias` elegido ya lo tiene otro usuario (`alias` es único en todo el sistema)

```json
{ "detail": "Alias already taken" }
```

Igual que en la creación: `user_id` y `cluster_profile` no son editables — si se mandan en el body, el backend los ignora silenciosamente.

---

## 3. Ver el perfil de un usuario

```
GET /api/v1/forums/profiles/{user_id}
```

Público (no requiere token). Se usa para mostrar el perfil de cualquier usuario dentro de forums (autor de un post, miembro de un grupo, etc.), no solo el propio.

**200 OK**

```json
{
  "user_id": 3,
  "alias": "maria_lopez",
  "bio": "Nueva bio",
  "avatar_url": "https://cdn.example.com/nuevo-avatar.png",
  "office_address": null
}
```

**404 Not Found** — si ese `user_id` no tiene perfil creado

```json
{ "detail": "Profile not found" }
```

---

## 4. Ver el perfil de un usuario + sus posts (timeline)

```
GET /api/v1/forums/profiles/{user_id}/timeline?limit=50&offset=0
```

**Nuevo.** Público (no requiere token). Como el `GET /forums/profiles/{user_id}`, pero además trae **todos** los posts que ese usuario haya publicado — incluye posts de grupo y anuncios (`is_ad: true`), a diferencia del feed global que los excluye — del más reciente al más antiguo. Pensado para una pantalla de "perfil público" tipo timeline, en una sola llamada.

`limit`/`offset` funcionan igual que en `/posts/global`, `/posts/recommended` y `/groups/{group_id}/posts`: paginado real para scroll infinito. `offset=0` trae los 50 posts más recientes; para pedir los siguientes, subí `offset` (ej. `offset=50` trae los siguientes 50, más viejos). Ningún post se pierde — se van pidiendo a medida que el usuario hace scroll.

**200 OK**

```json
{
  "profile": {
    "user_id": 3,
    "alias": "maria_lopez",
    "bio": "Nueva bio",
    "avatar_url": "https://cdn.example.com/nuevo-avatar.png",
    "office_address": null
  },
  "posts": [
    {
      "post_id": 17,
      "author_id": 3,
      "group_id": null,
      "title": "Mi primer control",
      "content": "Todo salió bien...",
      "is_ad": false,
      "created_at": "2026-07-11T04:41:14.892514Z"
    },
    {
      "post_id": 11,
      "author_id": 3,
      "group_id": 5,
      "title": "Pregunta en el grupo",
      "content": "¿Alguien más siente...?",
      "is_ad": false,
      "created_at": "2026-07-09T20:22:46.213138Z"
    }
  ]
}
```

`profile` es exactamente lo mismo que devuelve `GET /forums/profiles/{user_id}` (mismo objeto, byte a byte) — si ya lo tenés cacheado en el front no hace falta pedirlo aparte, pero esta ruta te lo trae igual por si armás la pantalla de perfil en una sola llamada.

**404 Not Found** — si ese `user_id` no tiene perfil creado

```json
{ "detail": "Profile not found" }
```

---

## Resumen de rutas

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/forums/profiles` | Sí | Crear mi perfil (una vez) |
| PATCH | `/forums/profiles/me` | Sí | Editar mi perfil (parcial) |
| GET | `/forums/profiles/{user_id}` | No | Ver el perfil de cualquier usuario |
| GET | `/forums/profiles/{user_id}/timeline` | No | Ver perfil + timeline de posts del usuario |
