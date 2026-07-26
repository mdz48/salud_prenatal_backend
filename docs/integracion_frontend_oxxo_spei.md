# Integración frontend: pago en efectivo/transferencia (OXXO y SPEI)

Complemento de [integracion_frontend_suscripciones.md](integracion_frontend_suscripciones.md). Aquí solo va **lo nuevo** para soportar que un doctor pague su mes con OXXO o SPEI, no solo con tarjeta. El backend ya está desplegado con estos cambios; falta el lado de la app.

## Qué cambió en una frase

Antes la app solo podía iniciar suscripciones recurrentes con tarjeta. Ahora el checkout acepta un `payment_mode`, y con `"one_time"` Stripe ofrece además **OXXO** (ficha en efectivo) y **SPEI** (transferencia). Estos dos son **asíncronos**: el doctor recibe una ficha/CLABE y paga después en tienda o desde su banco; la suscripción **no se activa al instante**.

## 1. El body del checkout ahora lleva `payment_mode`

`POST /api/v1/subscriptions/checkout-session`

```json
{
  "plan_type": "basic",
  "payment_mode": "one_time"
}
```

- `plan_type`: `"basic"` | `"premium"` (sin cambios).
- `payment_mode`:
  - `"recurring"` — suscripción con tarjeta, se renueva sola cada mes. **Es el default si se omite** (por eso la app hoy solo hace esto).
  - `"one_time"` — pago de **un solo mes**. En la página de Stripe el doctor elige tarjeta, **OXXO** o **SPEI**.

> **Acción mínima en la app (bloqueante):** hoy el request manda solo `{"plan_type": ...}`, así que siempre cae en `recurring` y OXXO/SPEI nunca aparece. Para ofrecer efectivo/transferencia hay que **incluir `payment_mode` en el body**.

La respuesta no cambia: `201` con `{ "checkout_url": "https://checkout.stripe.com/..." }`. La app solo abre esa URL en el navegador in-app, igual que hoy.

### UX sugerida

Un selector en la pantalla de plan: **"Tarjeta (renovación automática)"** vs **"Efectivo o transferencia (pago único de 1 mes)"**. El primero manda `recurring`, el segundo `one_time`. El método concreto (OXXO vs SPEI vs tarjeta suelta) se elige dentro de la página de Stripe, la app no lo decide.

## 2. OXXO/SPEI son asíncronos: el polling de 15s NO basta

Con tarjeta, el pago se confirma en segundos y el patrón de polling actual (`GET /subscriptions/me` cada 2s, ~15s máx.) funciona.

Con **OXXO/SPEI no**: al cerrar el checkout, el doctor **todavía no pagó** — tiene una ficha para pagar en las próximas ~72 h (OXXO) o una CLABE para transferir. El estado sigue en `pending` y solo pasa a `active` cuando el backend recibe el webhook `checkout.session.async_payment_succeeded`, que puede llegar **horas o días después**.

Por eso:

- El polling de 15s **siempre expirará** para OXXO/SPEI. No es un error, es lo esperado.
- El texto actual "Confirmando tu pago..." **engaña** en este flujo. Para `one_time`, tras volver del checkout la pantalla debería decir algo como: **"Genera y paga tu ficha OXXO / haz tu transferencia SPEI. Tu acceso se activa en cuanto se registre el pago (puede tardar hasta 72 h en OXXO, unos minutos en SPEI)."**
- Mantener el botón **"Ya pagué, verificar de nuevo"** (que reconsulta `GET /subscriptions/me`). Es el mecanismo correcto para cuando el doctor regrese a la app ya habiendo pagado.
- Opcional pero recomendado: revalidar el estado en `onResume` / al abrir la pantalla de suscripción, no solo con el timer.

> **Recordatorio del refresh de token (igual que en el doc principal):** cuando el estado por fin llegue a `active`, hay que llamar `POST /api/v1/users/refresh` y reemplazar el token guardado, porque el gating lee `subscription_status` desde el JWT. Esto aplica igual para OXXO/SPEI, solo que ocurre mucho después del checkout.

## 3. `GET /subscriptions/me` ahora trae `auto_renewal`

```json
{
  "status": "active",
  "plan_type": "basic",
  "current_period_end": "2026-08-15T00:00:00",
  "cancel_at_period_end": false,
  "auto_renewal": false
}
```

- **`auto_renewal`** (boolean) — distingue el tipo de pago:
  - `true` → suscripción recurrente con tarjeta; se cobra sola cada mes.
  - `false` → pagó **un mes** (OXXO/SPEI o tarjeta suelta). **No hay renovación automática**: al llegar `current_period_end` el acceso expira y el doctor debe volver a pagar.

> **Acción en la app:** el modelo actual (`SubscriptionStatusModel.fromJson`) **no parsea** este campo. Hay que agregarlo. Con `auto_renewal == false` y `status == "active"`, muestra en la pantalla de suscripción un aviso claro: **"Pago único — tu acceso vence el {current_period_end}. Renueva antes de esa fecha para no perder acceso."** Sin esto, el doctor de OXXO no tiene forma de saber que su acceso no se renueva solo.

- **`cancel_at_period_end`** (boolean) — ya documentado en el doc principal (§7). Aviso "tu plan se cancelará el {fecha}" mientras siga `active`. El modelo tampoco lo parsea hoy; conviene agregarlo en el mismo cambio.

## 4. Lo que NO cambia

- El deep link de retorno sigue igual: `saludprenatal://payment-callback/...`. No hay que registrar nada nuevo.
- Los endpoints gateados y el manejo global de `402` no cambian.
- El botón "Gestionar suscripción" (`portal-session`) es solo para recurrentes con tarjeta. Un pago OXXO/SPEI **no** tiene portal de Stripe (no hay suscripción viva que gestionar); si `auto_renewal == false`, oculta ese botón o, en su lugar, muestra "Renovar" (que reinicia el flujo de checkout).

## Resumen de la delta

| Área | Antes | Ahora |
|---|---|---|
| Body de checkout | `{plan_type}` | `{plan_type, payment_mode}` — `payment_mode: "one_time"` habilita OXXO/SPEI |
| Confirmación de pago | inmediata (tarjeta) | **asíncrona** en OXXO/SPEI: ficha/CLABE, se activa horas/días después |
| Polling post-checkout | 2s × 15s → dashboard | igual para tarjeta; en `one_time` expira siempre → mostrar instrucciones de ficha + "Ya pagué" |
| `GET /me` | `status, plan_type, current_period_end, cancel_at_period_end` | agrega **`auto_renewal`** |
| Aviso de vencimiento | no aplicaba (auto-renovación) | si `auto_renewal == false`: avisar que el acceso vence en `current_period_end` |

## Contratos actualizados (referencia rápida)

| Endpoint | Método | Auth | Body | Respuesta |
|---|---|---|---|---|
| `/api/v1/subscriptions/checkout-session` | POST | doctor | `{plan_type: "basic"\|"premium", payment_mode: "recurring"\|"one_time"}` | `{checkout_url}` |
| `/api/v1/subscriptions/me` | GET | doctor | — | `{status, plan_type, current_period_end, cancel_at_period_end, auto_renewal}` |
