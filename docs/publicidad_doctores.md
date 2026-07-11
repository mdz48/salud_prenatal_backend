# Publicidad de doctores intercalada en el feed

## Qué resuelve

Los doctores quieren darse a conocer publicando "recomendaciones" que se destaquen como **publicidad** mientras la paciente navega el feed social. Un doctor marca su post como anuncio al publicarlo; ese anuncio se **intercala** entre las publicaciones normales del feed de recomendaciones, se muestra a todas las usuarias por igual, y el front lo renderiza distinto gracias a un flag `is_ad`.

Depende de la feature de [recomendaciones por cluster](recomendaciones_por_cluster.md): los anuncios se inyectan sobre el feed `/posts/recommended`.

## Decisiones de diseño

- **Flag explícito** `is_ad` al publicar. Un doctor puede publicar normal (`is_ad=false`) o como publicidad (`is_ad=true`). No todo post de doctor es anuncio.
- **Gating por suscripción premium activa** (no por rol): solo doctores con `plan_type=premium` **y** `status=active` en el feature de [suscripciones Stripe](suscripciones_doctores_stripe.md) pueden marcar `is_ad=true`. Un doctor con plan básico, con la suscripción pendiente/vencida/cancelada, o sin fila de suscripción (legacy), recibe `HTTP 402 Payment Required`.
- **Tope semanal de 10 anuncios** por autor (ventana rolling de los últimos 7 días). El 11º intento en la ventana recibe `HTTP 429 Too Many Requests`.
- **Intercalado en el feed**: una sola lista mezclada; cada item lleva `is_ad`. Un anuncio tras cada `AD_EVERY = 4` posts normales. En feeds cortos (menos de 4 posts) el anuncio igual aparece al final, para que la publicidad no quede invisible.
- **Alcance global**: los anuncios **no** se filtran por cluster; salen a toda usuaria del feed (el doctor busca el máximo alcance).

## Cómo se marca y se protege

`POST /api/v1/forums/posts` acepta `is_ad` en el body. La validación vive en el caso de uso:

```
CreatePostUseCase.execute(post)
    │  post.is_ad == True
    ▼
IAdEligibilityLookup.is_premium_active(post.author_id)   → AdEligibilityAdapter → ISubscriptionRepository
    │  False (sin fila, o plan_type != premium, o status != active)
    ▼
AdPermissionError("La publicidad requiere suscripción premium activa")   → el controller lo mapea a HTTP 402
    │  True
    ▼
count_ads_by_author_since(author_id, ahora - 7 días) >= 10
    ▼
AdRateLimitError("Límite semanal de anuncios alcanzado (10)")   → el controller lo mapea a HTTP 429
```

Los posts normales (`is_ad=false`) no consultan elegibilidad ni cuentan anuncios previos.

> **Autoría vía JWT:** `POST /forums/posts` deriva el `author_id` del **token** (no del body). El gating de publicidad consulta la suscripción **real** del usuario autenticado, así que una paciente no puede publicar publicidad usando el id de un doctor. Ver [autoria_forums_jwt](autoria_forums_jwt.md).
>
> **Cómo un doctor se vuelve elegible:** no hay un endpoint propio de "activar publicidad" — el doctor paga el plan premium por el flujo normal de suscripciones: `POST /subscriptions/checkout-session {"plan_type": "premium"}` → paga en Stripe → el webhook activa `status=active`. Ver [suscripciones_doctores_stripe.md](suscripciones_doctores_stripe.md).

## Cómo se intercala

La clave es mantener el stream de posts normales limpio y **separado** de los anuncios, para que la inyección sea determinista:

1. Los feeds normales **excluyen** anuncios: `get_global_feed` y `get_feed_by_cluster` filtran `is_ad == False`.
2. `ForumsRepository.get_ads(limit)` trae los anuncios globales (`is_ad == True`, `group_id == None`), recientes primero.
3. El helper puro `interleave(posts, ads, every=4)` mezcla ambos: un anuncio tras cada 4 posts, hasta agotar anuncios, más uno al cierre si el feed es corto.
4. `GetRecommendedFeedUseCase` obtiene el feed base (por cluster o fallback global), pide los anuncios e intercala.

```
GET /forums/posts/recommended  (token de paciente)
        │
        ▼
GetRecommendedFeedUseCase.execute()
        │
        ├─ posts = feed base (por cluster o global) — SIN anuncios
        ├─ ads   = ForumsRepository.get_ads()
        ▼
interleave(posts, ads, every=4)
        │
        ▼
[ p, p, p, p, AD, p, p, ... ]   cada item con su is_ad
```

`/posts/global` queda como feed crudo sin anuncios; los anuncios solo se ven a través del feed de recomendaciones (que es el que navega la paciente).

## Cómo lo consume el front

Cada objeto del feed trae `is_ad` en `PostResponse`. El front:
- Renderiza los items con `is_ad=true` como tarjeta de **"Publicidad"** (estilo distinto, sello, etc.).
- El resto se muestra como publicación normal.

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `app/features/forums/domain/feed_interleave.py` | **Nuevo.** Helper puro `interleave(posts, ads, every)` |
| `app/features/forums/domain/post_entity.py` | Nuevo campo `is_ad: bool = False` |
| `app/features/forums/domain/ports.py` | `IAdEligibilityLookup.is_premium_active`; `IForumsRepository.get_ads`, `count_ads_by_author_since` |
| `app/features/forums/domain/exceptions.py` | **Nuevo.** `AdPermissionError`, `AdRateLimitError` |
| `app/features/forums/application/posts/create_post_usecase.py` | Depende de `ad_eligibility`; gatea `is_ad` a premium activo + tope semanal (`WEEKLY_AD_LIMIT = 10`) |
| `app/features/forums/application/posts/get_recommended_feed_usecase.py` | Intercala anuncios con `get_ads` + `interleave` (`AD_EVERY = 4`) |
| `app/features/forums/infrastructure/adapters/ad_eligibility_adapter.py` | **Nuevo.** Resuelve elegibilidad de anuncios (forums → subscriptions), reemplaza al antiguo `author_role_adapter.py` |
| `app/features/forums/infrastructure/repositories/forums_repository.py` | `get_ads`, `count_ads_by_author_since`; filtro `is_ad == False` en `get_global_feed` y `get_feed_by_cluster` |
| `app/features/forums/infrastructure/models/post_model.py` | Nueva columna `is_ad` (Boolean, default False, indexada) |
| `app/features/forums/infrastructure/schemas/forums_schemas.py` | `is_ad` en `PostCreate` y `PostResponse` |
| `app/features/forums/infrastructure/controllers/posts_controller.py` | Mapea `AdRateLimitError`→429, `AdPermissionError`→402 |
| `app/core/containers.py` | Registra `ad_eligibility_adapter` (reutiliza `subscription_repository`); lo inyecta en `create_post_use_case` |

No hay endpoints nuevos: la publicidad usa `POST /forums/posts` (con `is_ad`) y sale por `GET /forums/posts/recommended`.

## Migración de base de datos

`create_all` no altera tablas existentes. En bases ya desplegadas:

```sql
ALTER TABLE posts ADD COLUMN is_ad BOOLEAN NOT NULL DEFAULT 0;
```

En los tests, SQLite se crea desde cero, no requiere migración.

## Tests

- `tests/test_forums/test_feed_interleave.py` — helper puro (sin anuncios, intervalo, feed corto, más anuncios que huecos).
- `tests/test_forums/test_ads.py` — gating de `is_ad` en `CreatePostUseCase` (sin premium activo, tope semanal) e intercalado en `GetRecommendedFeedUseCase`.
- `tests/test_forums/test_ads_repository.py` — `get_ads`, `count_ads_by_author_since` (ventana de 7 días, por autor) y exclusión de anuncios en los feeds normales.
- `tests/test_forums/test_ad_eligibility_adapter.py` — `is_premium_active` para cada combinación de plan/estado (premium+active, basic+active, premium+pending, premium+past_due, sin fila).
- `tests/test_forums_cluster_e2e.py` — end to end: doctor con plan básico activo intenta `is_ad=true` → `402`; con premium activo → `201` y aparece intercalado; el 11º anuncio de la semana → `429`; paciente que intenta `is_ad=true` → `402`.
