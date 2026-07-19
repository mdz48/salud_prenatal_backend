# Suscripciones de doctores con Stripe

## Qué resuelve

Los doctores deben pagar una suscripción mensual para usar el sistema: **básica $399 MXN/mes** o **premium $499 MXN/mes**. El registro sigue siendo gratis; lo que se bloquea son las acciones propias del doctor (evaluar riesgo, agendar citas) hasta que la suscripción esté activa.

## Arquitectura

Feature hexagonal nuevo `app/features/subscriptions/`, dentro del monolito (no microservicio). Stripe queda aislado tras un port `IPaymentGateway`, igual que el ML externo está aislado tras `IMLPredictionService` (`MlPredictionServiceAdapter`). Un microservicio aparte solo agregaría deploy doble y consistencia distribuida sin beneficio real para este caso.

```
app/features/subscriptions/
├── domain/
│   ├── subscription_entity.py      # SubscriptionEntity (pydantic)
│   └── ports.py                    # ISubscriptionRepository, IPaymentGateway, InvalidWebhookError
├── application/
│   ├── dtos.py                     # CheckoutSessionResult, PaymentEventDTO, SubscriptionStatusDTO
│   ├── create_checkout_session_usecase.py
│   ├── get_my_subscription_usecase.py
│   └── handle_payment_event_usecase.py
└── infrastructure/
    ├── models/subscription_model.py
    ├── repositories/subscription_repository.py
    ├── adapters/
    │       ├── stripe_gateway_adapter.py    # parser de webhooks y portals
    │       └── stripe_checkout_strategies.py # Implementa ICheckoutStrategy (recurring y one_time)
    ├── controllers/subscription_controller.py
    ├── schemas/subscription_schema.py
    └── routes/subscription_router.py
```

Cross-feature: `users` no importa nada de `subscriptions` directamente. Define sus propios ports (`ISubscriptionInitializer`, `ISubscriptionStatusLookup` en `app/features/users/domain/ports.py`) implementados por un adapter propio (`app/features/users/infrastructure/adapters/subscription_initializer_adapter.py`) que envuelve `SubscriptionRepository`. Mismo patrón que `MedicalRecordLookupAdapter`.

## Modelo de datos

Tabla `subscriptions`, FK a `users.user_id` con `UNIQUE(user_id)` — no a `doctor_id`. `get_current_user`/JWT y la correlación de webhooks operan sobre `user_id`; "solo los doctores pagan" lo garantiza el flujo (la fila solo se crea en `RegisterDoctorUseCase`), no la FK.

| Columna | Tipo | Notas |
|---|---|---|
| `subscription_id` | PK | |
| `user_id` | FK único | |
| `plan_type` | `PlanTypeEnum` nullable | `basic` / `premium`; nulo hasta el primer checkout |
| `status` | `SubscriptionStatusEnum` | `pending` (default) / `active` / `past_due` / `canceled` |
| `stripe_customer_id` | string nullable | |
| `stripe_subscription_id` | string nullable, único | |
| `current_period_end` | datetime nullable | |
| `cancel_at_period_end` | boolean, default false | |

Enums en [`app/core/enums.py`](../app/core/enums.py). **Los montos viven solo en Stripe** (objetos Price); el backend guarda únicamente los Price IDs por variable de entorno.

## Flujo completo

```
POST /doctors/register
        │
        ▼
RegisterDoctorUseCase.execute()
   crea Usuario + Doctor
        │
        ▼
ISubscriptionInitializer.create_pending(user_id)   → fila subscriptions status=pending
        │
--- luego, el doctor ---
        ▼
POST /users/login → 200, subscription_status: "pending" en la respuesta
        ▼
POST /subscriptions/checkout-session {"plan_type": "basic", "payment_mode": "recurring"}
        │  (RoleChecker: solo doctor)
        ▼
CreateCheckoutSessionUseCase
   get-or-create pending (backfill si el doctor es previo a este feature)
        ▼
StripeRecurringCheckoutStrategy.create_checkout_session()
   stripe.checkout.Session.create(mode="subscription", ...)
   client_reference_id=user_id, metadata={user_id, plan_type}, subscription_data.metadata=igual
        ▼
{"checkout_url": "https://checkout.stripe.com/..."}
        │
--- doctor paga en la página hosteada de Stripe ---
        ▼
Stripe envía webhook → POST /subscriptions/webhook
        ▼
StripeGatewayAdapter.parse_webhook_event()
   stripe.Webhook.construct_event() verifica firma (Stripe-Signature + STRIPE_WEBHOOK_SECRET)
   normaliza a PaymentEventDTO (agnóstico de Stripe)
        ▼
HandlePaymentEventUseCase
   localiza la fila (por stripe_subscription_id, fallback por user_id en metadata)
   aplica transición → status=active, guarda stripe_customer_id/stripe_subscription_id/plan_type
        │
--- de vuelta en el backend ---
        ▼
GET /subscriptions/me → {"status": "active", "plan_type": "basic", ...}
Endpoints gateados (ej. risk-evaluation) → 200 en vez de 402
```

## Webhooks: eventos manejados

| Evento Stripe | `PaymentEventDTO.kind` | Transición |
|---|---|---|
| `checkout.session.completed` (subscription) | `checkout_completed` | guarda `stripe_customer_id`, `stripe_subscription_id`, `plan_type`; `status=active` |
| `checkout.session.completed` (payment) o `checkout.session.async_payment_succeeded` | `one_time_payment_succeeded` | guarda `stripe_customer_id`, `plan_type`; `status=active`, `current_period_end += 30 days` |
| `invoice.paid` | `payment_succeeded` | `status=active`, actualiza `current_period_end` |
| `invoice.payment_failed` | `payment_failed` | `status=past_due` |
| `customer.subscription.updated` | `subscription_updated` | sincroniza `status` desde el status de Stripe |
| `customer.subscription.deleted` | `subscription_canceled` | `status=canceled` |
| cualquier otro | — | `parse_webhook_event` devuelve `None`; el use case no hace nada, responde 200 |

Correlación: por `stripe_subscription_id`; si no hay fila con ese id, fallback por `user_id` (viene en `client_reference_id`/`metadata`). Todas las transiciones son idempotentes — reprocesar el mismo evento no rompe nada.

**Detalle de implementación importante**: los objetos que devuelve el SDK `stripe` (`StripeObject`) **no soportan `.get()`** como un dict — solo acceso por atributo o índice (`obj["key"]`). El adapter usa un helper `_f(obj, key, default=None)` que hace `getattr(obj, key, default)` para leer campos anidados (`metadata`, `lines.data[0].period`, etc.) de forma segura. Ver [`test_stripe_gateway_adapter.py`](../tests/test_subscriptions/test_stripe_gateway_adapter.py) — construye `stripe.Event` reales (no dicts) para que este detalle quede cubierto por tests.

## Gating

`require_active_subscription` en [`app/core/dependencies.py`](../app/core/dependencies.py): dependency adicional (no reemplaza `RoleChecker`). Solo evalúa cuando `role == doctor`; otros roles pasan sin chequeo. Sin fila o `status != active` → **HTTP 402 Payment Required**.

Aplicado junto a los checks de rol existentes en:
- `medical_record_router`: `evaluate_risk`, `update_medical_record`
- `appointment_router`: `create_appointment`, `update_appointment`, `delete_appointment`

**Pendiente / fuera de alcance**: `doctor_router` (gestión de pacientes, recepcionistas) hoy no tiene ningún auth dependency — agregarlo sería un cambio de comportamiento aparte, no se tocó en este feature.

## Variables de entorno

Todas se leen de forma lazy (dentro de los métodos del adapter, nunca a nivel de módulo) para no romper `tests/conftest.py`, que importa `main` sin estas variables definidas.

| Variable | Uso |
|---|---|
| `STRIPE_PRIVATE_KEY` | Secret key de Stripe (`sk_test_...` / `sk_live_...`) — **no** la publicable (`pk_...`) |
| `STRIPE_WEBHOOK_SECRET` | Firma del endpoint de webhook (`whsec_...`), la da `stripe listen` en local o el dashboard en producción |
| `STRIPE_PRICE_ID_BASIC` | Price ID (`price_...`) del plan básico recurrente |
| `STRIPE_PRICE_ID_PREMIUM` | Price ID (`price_...`) del plan premium recurrente |
| `STRIPE_PRICE_ID_BASIC_ONETIME` | Price ID (`price_...`) del plan básico pago único |
| `STRIPE_PRICE_ID_PREMIUM_ONETIME` | Price ID (`price_...`) del plan premium pago único |
| `FRONTEND_URL` | Base para `success_url`/`cancel_url` del Checkout |

## Migración de base de datos

`create_all` no altera tablas existentes, así que la tabla `subscriptions` se crea sola en un despliegue nuevo. En una base ya desplegada sin Alembic no hay backfill automático de filas — por eso `CreateCheckoutSessionUseCase` hace *get-or-create*: si un doctor registrado antes de este feature pide checkout, se le crea la fila `pending` en ese momento.

**Columna nueva `cancel_at_period_end`** (agregada para el feature de Customer Portal): en una base ya desplegada hay que correr manualmente:

```sql
ALTER TABLE subscriptions ADD COLUMN cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE;
```

**Orden importa**: corre este `ALTER TABLE` **antes o junto con** el deploy del código nuevo, no después. El código nuevo lee esta columna en cada `SELECT` sobre `Subscription` — si el deploy de código llega antes que la columna exista, toda la feature de suscripciones se rompe (`column subscriptions.cancel_at_period_end does not exist`) hasta que corras el `ALTER TABLE`. Como es una columna con `DEFAULT`, agregarla antes es seguro: el código viejo simplemente la ignora.

## Tests

- `tests/test_subscriptions/` — unit tests de los 3 use cases (ports mockeados) + `test_stripe_gateway_adapter.py` (parseo de eventos Stripe reales, sin red).
- `tests/test_users/test_register_doctor_usecase.py` — verifica que el registro crea la suscripción pendiente.
- `tests/test_users/test_user_usecases.py` — login incluye `subscription_status`.
- `tests/test_medical_record_e2e.py`, `tests/test_forums_cluster_e2e.py` — actualizados para activar la suscripción del doctor (fixture `activate_subscription` en `conftest.py`, escribe directo en la BD de test) antes de pegarle a endpoints gateados.
- Stripe **nunca** se llama de verdad en tests — el SDK solo se ejercita indirectamente reconstruyendo objetos `stripe.Event`/`stripe.checkout.Session` con `construct_from`.

Verificación manual end-to-end (modo test de Stripe) documentada en [integracion_frontend_suscripciones.md](integracion_frontend_suscripciones.md).

## Ledger de transacciones (service_pagos)

Cada evento de webhook aplicado se registra en la tabla `payment_transactions`
(una fila por `stripe_event_id`, UNIQUE). Esto da:

- **Idempotencia**: Stripe reintenta webhooks ante timeouts/5xx; si el evento ya
  está en el ledger, `HandlePaymentEventUseCase` lo ignora. (Antes, cada reintento
  de un pago one-time sumaba +30 días a `current_period_end`.)
- **Historial**: `GET /api/v1/subscriptions/payments` (rol doctor) devuelve los
  pagos del usuario autenticado: `kind`, `amount_cents`, `currency`, `created_at`.

El ledger se escribe después de aplicar la transición a la suscripción; si el
proceso muere entre ambos commits, el reintento de Stripe re-aplica el evento
(trade-off documentado en el plan 2026-07-16-payment-transactions-ledger).
