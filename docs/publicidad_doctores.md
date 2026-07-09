# Publicidad de doctores intercalada en el feed

## Qué resuelve

Los doctores quieren darse a conocer publicando "recomendaciones" que se destaquen como **publicidad** mientras la paciente navega el feed social. Un doctor marca su post como anuncio al publicarlo; ese anuncio se **intercala** entre las publicaciones normales del feed de recomendaciones, se muestra a todas las usuarias por igual, y el front lo renderiza distinto gracias a un flag `is_ad`.

Depende de la feature de [recomendaciones por cluster](recomendaciones_por_cluster.md): los anuncios se inyectan sobre el feed `/posts/recommended`.

## Decisiones de diseño

- **Flag explícito** `is_ad` al publicar. Un doctor puede publicar normal (`is_ad=false`) o como publicidad (`is_ad=true`). No todo post de doctor es anuncio.
- **Gating por rol**: solo usuarios con rol `doctor` pueden marcar `is_ad=true`. Una paciente que lo intente recibe `HTTP 400`.
- **Intercalado en el feed**: una sola lista mezclada; cada item lleva `is_ad`. Un anuncio tras cada `AD_EVERY = 4` posts normales. En feeds cortos (menos de 4 posts) el anuncio igual aparece al final, para que la publicidad no quede invisible.
- **Alcance global**: los anuncios **no** se filtran por cluster; salen a toda usuaria del feed (el doctor busca el máximo alcance).

## Cómo se marca y se protege

`POST /api/v1/forums/posts` acepta `is_ad` en el body. La validación vive en el caso de uso:

```
CreatePostUseCase.execute(post)
    │  post.is_ad == True
    ▼
IAuthorRoleLookup.get_role(post.author_id)   → AuthorRoleAdapter → UserRepository
    │  rol != "doctor"
    ▼
ValueError("Solo los doctores pueden publicar publicidad")   → el controller lo mapea a HTTP 400
```

Los posts normales (`is_ad=false`) no consultan el rol.

> **Autoría vía JWT:** `POST /forums/posts` deriva el `author_id` del **token** (no del body). El gating de publicidad consulta el rol **real** del usuario autenticado, así que una paciente no puede publicar publicidad usando el id de un doctor. Ver [autoria_forums_jwt](autoria_forums_jwt.md).

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
| `app/features/forums/domain/ports.py` | Nuevo `IAuthorRoleLookup`; nuevo `IForumsRepository.get_ads` |
| `app/features/forums/application/posts/create_post_usecase.py` | Depende de `author_role_lookup`; gatea `is_ad` a rol doctor |
| `app/features/forums/application/posts/get_recommended_feed_usecase.py` | Intercala anuncios con `get_ads` + `interleave` (`AD_EVERY = 4`) |
| `app/features/forums/infrastructure/adapters/author_role_adapter.py` | **Nuevo.** Resuelve el rol del autor (forums → users) |
| `app/features/forums/infrastructure/repositories/forums_repository.py` | `get_ads`; filtro `is_ad == False` en `get_global_feed` y `get_feed_by_cluster` |
| `app/features/forums/infrastructure/models/post_model.py` | Nueva columna `is_ad` (Boolean, default False, indexada) |
| `app/features/forums/infrastructure/schemas/forums_schemas.py` | `is_ad` en `PostCreate` y `PostResponse` |
| `app/core/containers.py` | Registra `author_role_adapter`; lo inyecta en `create_post_use_case` |

No hay endpoints nuevos: la publicidad usa `POST /forums/posts` (con `is_ad`) y sale por `GET /forums/posts/recommended`.

## Migración de base de datos

`create_all` no altera tablas existentes. En bases ya desplegadas:

```sql
ALTER TABLE posts ADD COLUMN is_ad BOOLEAN NOT NULL DEFAULT 0;
```

En los tests, SQLite se crea desde cero, no requiere migración.

## Tests

- `tests/test_forums/test_feed_interleave.py` — helper puro (sin anuncios, intervalo, feed corto, más anuncios que huecos).
- `tests/test_forums/test_ads.py` — gating de `is_ad` en `CreatePostUseCase` e intercalado en `GetRecommendedFeedUseCase`.
- `tests/test_forums/test_ads_repository.py` — `get_ads` y exclusión de anuncios en los feeds normales.
- `tests/test_forums/test_author_role_adapter.py` — resolución del rol del autor.
- `tests/test_forums_cluster_e2e.py` — end to end: doctor publica anuncio → aparece intercalado y marcado `is_ad` en el feed de la paciente; paciente que intenta `is_ad=true` → `400`.
