# Chat — mensajes leídos (integración frontend)

## Qué cambió

`GET /api/v1/chat/history/{other_user_id}` ahora **marca como leídos** (`is_read=true`)
los mensajes que `other_user_id` le envió al usuario autenticado, como efecto
secundario de consumir la conversación. No hay endpoint nuevo ni cambio de contrato:
mismas rutas, mismos schemas.

## Semántica

- `is_read` es **por receptor**: un mensaje A→B con `is_read=true` significa "B ya lo vio".
- Al pedir history solo se marcan los mensajes **dirigidos a quien consulta**
  (`sender=other_user`, `receiver=usuario del token`). Los mensajes que el usuario
  envió no se tocan — esos los marca el otro usuario cuando abra su lado del chat.
- No existe "leído para ambos": cada lado tiene su propio estado.
- La respuesta del history ya viene con el estado actualizado: los mensajes entrantes
  llegan con `is_read: true`.

## Flujo recomendado

1. Usuario abre la conversación → `GET /api/v1/chat/history/{other_user_id}`.
   Esto ya deja en 0 los no-leídos de ese contacto en el backend.
2. Refrescar `GET /api/v1/chat/inbox` (o decrementar localmente): el
   `unread_count` de ese contacto queda en `0`.

## Caso borde: mensaje por WebSocket con el chat abierto

Un mensaje que llega por WS mientras la conversación está visible queda
`is_read=false` en la base hasta el próximo `GET /history`. El payload del WS
trae `"is_read": false`. Si quieres que el contador quede exacto sin cerrar el
chat, al recibir un mensaje por WS con esa conversación visible vuelve a llamar
`GET /history/{other_user_id}` (marca y devuelve el estado ya actualizado).
Si solo actualizas la UI localmente, el `unread_count` del inbox mostrará 1
hasta el siguiente history.

## Resumen de contrato

| Acción | Efecto en `is_read` |
|--------|---------------------|
| `GET /chat/history/{other}` | Marca leídos los mensajes de `other` → tú. Respuesta ya actualizada. |
| `GET /chat/inbox` | Solo lectura. `unread_count` = mensajes recibidos no leídos por contacto. |
| Mensaje por WS | Se guarda con `is_read=false`. |
| Enviar mensaje | Sin efecto sobre lo que tú tienes sin leer. |
