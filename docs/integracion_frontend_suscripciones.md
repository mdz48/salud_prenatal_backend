# Integración frontend: suscripciones de doctores

Guía para el equipo de frontend/app móvil. Arquitectura y detalles de backend en [suscripciones_doctores_stripe.md](suscripciones_doctores_stripe.md).

## Resumen del flujo

1. Doctor se registra normal — **no cambia nada** en el formulario de registro.
2. Doctor hace login — la respuesta ahora trae `subscription_status`.
3. Si no es `"active"`, el front debe mandar al doctor a una pantalla de pago (o bloquear ciertas acciones) en vez de dejarlo usar el sistema con normalidad.
4. El front pide al backend una URL de Checkout y **redirige/abre esa URL** — el formulario de pago lo hostea Stripe, el front no construye ningún formulario de tarjeta.
5. Tras pagar, Stripe notifica al backend por su cuenta (webhook). El front no tiene que "avisar" que se pagó — solo debe volver a consultar el estado.

## 1. Login: nuevo campo `subscription_status`

`POST /api/v1/users/login`

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user_id": 42,
  "role": "doctor",
  "patient_id": null,
  "doctor_id": 10,
  "medical_record_id": null,
  "receptionist": null,
  "subscription_status": "pending"
}
```

`subscription_status` solo viene poblado para `role == "doctor"`. Para pacientes/recepcionistas/admin es `null` — **no aplica gating a esos roles**.

Valores posibles: `"pending"` | `"active"` | `"past_due"` | `"canceled"`.

**Recomendación de UX**: si `role == "doctor"` y `subscription_status != "active"`, redirigir a la pantalla de suscripción inmediatamente después del login, antes de mostrar el dashboard normal.

## 2. Consultar el estado en cualquier momento

`GET /api/v1/subscriptions/me` — requiere `Authorization: Bearer <token>` de un doctor.

```json
{
  "status": "active",
  "plan_type": "basic",
  "current_period_end": "2026-08-07T00:00:00",
  "cancel_at_period_end": false,
  "auto_renewal": true
}
```

Si el doctor nunca inició un checkout, `plan_type` y `current_period_end` vienen `null`, `status` es `"pending"`, `cancel_at_period_end` es `false` y `auto_renewal` es `false`.
El campo `auto_renewal` permite saber si el doctor está en el plan recurrente (suscripción) o pagó un mes manualmente (OXXO/SPEI). Si `auto_renewal` es `false` pero `status` es `active`, la suscripción expirará al final de `current_period_end`.

Útil para refrescar el estado sin re-loguear (ej. al volver de la pantalla de pago, o en un pull-to-refresh de la pantalla de suscripción).

## 3. Iniciar el pago

`POST /api/v1/subscriptions/checkout-session` — requiere `Authorization: Bearer <token>` de un doctor.

Body:
```json
{ 
  "plan_type": "basic",
  "payment_mode": "recurring"
}
```
- `plan_type` acepta `"basic"` o `"premium"`.
- `payment_mode` acepta `"recurring"` (tarjeta/suscripción, default si se omite) o `"one_time"` (pago mes a mes con efectivo, transferencia o tarjeta).

Respuesta (201):
```json
{ "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_..." }
```

**El front solo debe abrir/redirigir a `checkout_url`.** Es una página completa hosteada por Stripe (no un iframe embebido ni un form propio). En app móvil, abrirla en un navegador in-app (Chrome Custom Tabs en Android / `SFSafariViewController` en iOS) — **no** en un WebView restringido que bloquee redirects, porque Stripe puede redirigir a 3D Secure.

## 4. Volver del pago (success / cancel) — deep link configurado ✅

**Estado actual en producción**: el backend tiene `FRONTEND_URL=saludprenatal://payment-callback` (ya configurado, confirmado funcionando). Stripe redirige a:

- Éxito: `saludprenatal://payment-callback/subscription/success?session_id={CHECKOUT_SESSION_ID}`
- Cancelación: `saludprenatal://payment-callback/subscription/cancel`

El esquema `saludprenatal://` lo reconoce el sistema operativo (Android/iOS) como deep link de la app — el navegador in-app se cierra solo y trae la app al frente al detectar la redirección, sin que el usuario tenga que salir manualmente.

**Verifica que tu intent filter (Android) / Associated Domain (iOS) matchee exacto**: esquema `saludprenatal`, host `payment-callback`, y las dos rutas `/subscription/success` y `/subscription/cancel`. Un mismatch de path es la causa más común de que el deep link no abra la app aunque el esquema esté bien registrado.

`session_id` en la URL de éxito **no confirma el pago por sí solo** — es solo para mostrar un mensaje ("procesando tu pago..."). La confirmación real llega por el webhook al backend, que puede tardar unos segundos. Patrón correcto en la pantalla de éxito:

```
1. Mostrar "Confirmando tu pago..."
2. Hacer polling a GET /subscriptions/me cada 2s (máx. ~15s)
3. Cuando status == "active":
   a. Llamar POST /api/v1/users/refresh con el token ACTUAL (Bearer).
   b. Reemplazar el token guardado por el `access_token` que devuelve.
   c. Mostrar éxito y navegar al dashboard.
4. Si pasan 15s sin confirmar → mostrar "Tu pago se está procesando, te avisaremos" (no es un error, solo tardó) + botón "Ya pagué, verificar de nuevo" (que reintenta desde el paso 2).
```

> **Importante — por qué el refresh:** el backend gatea los endpoints (citas, expedientes) leyendo el `subscription_status` que viene *dentro del JWT*, no consultándolo en vivo. Ese claim solo se actualiza al emitir un token nuevo. Tras pagar, `GET /me` ya dice "active" (lo lee en vivo), pero **el token viejo sigue diciendo "pending"** → los endpoints gateados darían 402. Por eso, al confirmarse el pago, hay que pedir un token nuevo con `POST /users/refresh` y reemplazar el guardado. Sin ese paso, el doctor pagó pero seguiría bloqueado ~30 min (hasta que el token expire y re-loguee).

En la pantalla de cancelación, simplemente ofrecer reintentar (volver a llamar `checkout-session`).

## 5. Qué endpoints quedan bloqueados sin suscripción activa

Con `subscription_status != "active"`, estos endpoints devuelven **`402 Payment Required`** en vez de su respuesta normal:

- `POST /api/v1/medical-records/{medical_record_id}/risk-evaluation`
- `PUT /api/v1/medical-records/{medical_record_id}`
- `POST /api/v1/appointments/`
- `PUT /api/v1/appointments/{appointment_id}`
- `DELETE /api/v1/appointments/{appointment_id}`

Cuerpo del 402:
```json
{ "detail": "Active subscription required. Current status: pending" }
```

**El front debe interceptar 402 globalmente** (en el interceptor de HTTP que ya maneje 401), y en vez de mostrar un error genérico, redirigir a la pantalla de suscripción. No hace falta parsear el `detail` — el status code basta para decidir la redirección.

Estos endpoints **no** están bloqueados (el doctor puede seguir usándolos aunque no pague, por ahora): registrar receptionists, ver pacientes, generar código de invitación (`/doctors/{doctor_id}/...`). Esto es una decisión temporal del backend, puede cambiar.

Nota: si una recepcionista crea/edita/borra una cita, el gating **no** verifica la suscripción del doctor que la emplea (solo bloquea si el rol del propio token es doctor). Es un hueco conocido, aceptado por ahora — no depender de que quede bloqueado en ese caso.

## 6. Planes: diferencia actual entre básico y premium

**Por ahora, ninguna a nivel de funcionalidad.** El backend solo guarda qué plan eligió el doctor (`plan_type`); ambos dan el mismo acceso al sistema. Si más adelante se definen features exclusivas de premium, se avisará qué endpoints cambian.

## 7. Gestionar suscripción (cancelar / cambiar de plan)

`POST /api/v1/subscriptions/portal-session` — requiere `Authorization: Bearer <token>` de un doctor. Sin body.

Respuesta (201):
```json
{ "portal_url": "https://billing.stripe.com/p/session/..." }
```

Respuesta (400) si el doctor nunca completó un checkout (no tiene un customer de Stripe todavía):
```json
{ "detail": "No active Stripe customer for this user" }
```

**Un solo botón "Gestionar suscripción"** en la pantalla de suscripción — no separes "Cancelar" de "Cambiar plan" en tu UI. El portal hosteado por Stripe ya muestra ambas opciones en la misma pantalla. Abre `portal_url` en el mismo navegador in-app que ya usas para `checkout_url`.

**Retorno**: al terminar en el portal, Stripe redirige a `saludprenatal://payment-callback/subscription/me` — mismo deep link que ya tienes registrado. Al recibirlo, refresca `GET /subscriptions/me` (no hace falta un patrón de polling nuevo, es el mismo que ya usas después del checkout).

**Campo nuevo en `GET /subscriptions/me`**: `cancel_at_period_end` (boolean).

```json
{
  "status": "active",
  "plan_type": "premium",
  "current_period_end": "2026-08-07T00:00:00",
  "cancel_at_period_end": true
}
```

Si `cancel_at_period_end` es `true` mientras `status` sigue siendo `"active"`, el doctor **ya canceló pero conserva acceso** hasta `current_period_end` — muéstrale un aviso tipo "Tu plan se cancelará el {current_period_end}" en vez de tratarlo como si ya hubiera perdido acceso. Solo cuando `status` cambie a `"canceled"` (después de esa fecha) debe verse como cancelado de verdad.

## Resumen de contratos (referencia rápida)

| Endpoint | Método | Auth | Body | Respuesta |
|---|---|---|---|---|
| `/api/v1/users/login` | POST | — | `{email, password}` | agrega `subscription_status` |
| `/api/v1/users/refresh` | POST | token válido | — | `{access_token, token_type, subscription_status}` |
| `/api/v1/subscriptions/me` | GET | doctor | — | `{status, plan_type, current_period_end, cancel_at_period_end, auto_renewal}` |
| `/api/v1/subscriptions/checkout-session` | POST | doctor | `{plan_type: "basic"\|"premium", payment_mode: "recurring"\|"one_time"}` | `{checkout_url}` |
| `/api/v1/subscriptions/portal-session` | POST | doctor | — | `{portal_url}` |

Cualquier endpoint de doctor puede responder `402` si la suscripción no está activa — manejarlo como caso global, no por endpoint.
