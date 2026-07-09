# Autoría de forums derivada del JWT

## Qué resuelve

Los cinco endpoints de escritura de `forums` tomaban la identidad del autor **del body** (`author_id`, `user_id`, `created_by`, `reporter_id`) sin autenticación. Cualquiera podía publicar, comentar, crear grupos o reportar **haciéndose pasar por otro usuario**. Ahora la identidad se deriva del **token JWT** y el campo se eliminó del contrato de request.

## Decisiones

- **Alcance**: los cinco POST de forums.
- **Contrato**: el campo de identidad se **quita** de cada schema `*Create`; el front deja de enviarlo. Imposible de falsificar.
- **Fuga de cluster**: `ProfileResponse` deja de exponer `cluster_profile` (dato derivado de información médica) en el `GET /forums/profiles/{user_id}` público.

## Patrón aplicado

Igual que los GET `/posts/recommended` y `/groups/recommended`, cada POST ahora:
1. **Router**: `current_user: UserEntity = Depends(get_current_user)`, pasa `current_user.user_id` al controller.
2. **Controller**: recibe el id como parámetro y lo asigna en la entidad (`PostEntity(**data.model_dump(), author_id=author_id)`), ignorando cualquier valor del body.
3. **Schema**: sin el campo de identidad.

Los usecases y repositorios **no cambian**: reciben la entidad ya poblada.

## Endpoints

| Endpoint | Campo eliminado del body | Ahora |
|----------|--------------------------|-------|
| `POST /forums/posts` | `author_id` | del token |
| `POST /forums/comments` | `author_id` | del token |
| `POST /forums/profiles` | `user_id` | del token |
| `POST /forums/groups` | `created_by` | del token |
| `POST /forums/reports` | `reporter_id` | del token |

Todos exigen `Authorization: Bearer <token>` → sin token responden `401`.

## Efecto en la publicidad

El gating de `is_ad` en `CreatePostUseCase` queda blindado: `get_role(author_id)` consulta el rol **real** del usuario autenticado, ya no un id arbitrario del body. Ver [publicidad_doctores.md](publicidad_doctores.md).

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `app/features/forums/infrastructure/schemas/forums_schemas.py` | Quitados los 5 campos de identidad de los `*Create`; `cluster_profile` fuera de `ProfileResponse` |
| `app/features/forums/infrastructure/routes/{posts,profiles,groups,reports}_router.py` | `Depends(get_current_user)` en los 5 POST |
| `app/features/forums/infrastructure/controllers/{posts,profiles,groups,reports}_controller.py` | Cada método de creación recibe el id y lo asigna |

Sin cambios de base de datos. Guía para el front: [IAContext/frontend_social_clusters_y_publicidad.md](../IAContext/frontend_social_clusters_y_publicidad.md).

## Tests

- `tests/test_forums_cluster_e2e.py` — creaciones con token del autor, sin id en body; `401` sin token; `ProfileResponse` sin `cluster_profile`.
- `tests/test_forums/test_author_from_token.py` — el id lo pone el token, no el body.
