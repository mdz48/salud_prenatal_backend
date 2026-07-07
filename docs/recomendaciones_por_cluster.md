# Recomendaciones sociales por cluster de riesgo

## Qué resuelve

Cuando una paciente entra al apartado social de la app móvil, ve **publicaciones y grupos de personas de su mismo cluster de riesgo**, no un feed genérico. Ejemplo: una paciente en el cluster de riesgo metabólico ve posts de otras embarazadas contando su día a día bajando de peso, y grupos dedicados a ese tema.

## De dónde sale el cluster

El microservicio `machine_learning_service` expone `POST /predict`, que devuelve `risk_cluster` (entero 0–3):

| Cluster | Significado |
|---------|-------------|
| 0 | Primigestas sanas (riesgo bajo-medio) |
| 1 | Alto riesgo hipertensivo / preeclampsia (crítico) |
| 2 | Multíparas sanas (riesgo bajo) |
| 3 | Riesgo metabólico / obesidad (alto) |

El backend ya persistía ese resultado en la tabla `risk_predictions` (una fila por evaluación) mediante `EvaluatePatientRiskUseCase`. Esta feature toma ese cluster y lo copia al **perfil social** de la paciente (`social_profiles.cluster_profile`), para luego filtrar contenido.

El valor guardado es el entero como texto (`"0"`–`"3"`). El front mapea esos códigos a etiquetas legibles.

## Decisiones de diseño

- **Asignación híbrida**: el cluster se sincroniza al perfil social en dos momentos, para cubrir cualquier orden de eventos (perfil creado antes o después de la primera evaluación):
  1. Cada vez que el doctor evalúa el riesgo y el resultado es `ok`.
  2. Al crear el perfil social (si ya existe una evaluación previa exitosa).
- **El cluster nunca lo manda el cliente.** Se deriva solo del ML; el campo se ignora si viene en el request de crear perfil.
- **Fallback seguro**: si la paciente aún no tiene cluster (nunca evaluada), los endpoints de recomendación devuelven el feed global / todos los grupos. Siempre ve contenido.

## Flujo

```
Doctor pulsa "evaluar riesgo"
        │
        ▼
EvaluatePatientRiskUseCase.execute()
        │  status == "ok" y prediction["risk_cluster"] presente
        ▼
ISocialClusterPort.update_cluster(user_id, "3")   (nunca rompe la evaluación: try/except)
        │
        ▼
SocialClusterAdapter → ForumsRepository.update_cluster_profile()
        │   (si el usuario no tiene perfil social todavía, es no-op)
        ▼
social_profiles.cluster_profile = "3"

--- luego, desde la app móvil ---

Paciente abre el apartado social (token JWT)
        │
        ▼
GET /forums/posts/recommended     GET /forums/groups/recommended
        │                                 │
        ▼                                 ▼
GetRecommendedFeedUseCase          GetRecommendedGroupsUseCase
   lee perfil → cluster                lee perfil → cluster
        │                                 │
   con cluster → get_feed_by_cluster  con cluster → get_groups_by_cluster
   sin cluster / vacío → get_global_feed  sin cluster / vacío → get_groups
```

Alternativamente, si la paciente crea su perfil social **después** de haber sido evaluada:

```
POST /forums/profiles
        ▼
CreateProfileUseCase.execute()
        ▼
IPatientClusterLookup.get_cluster_by_user_id(user_id)
        ▼
PatientClusterAdapter:  user → patient → expediente → última predicción "ok" → "3"
        ▼
perfil creado con cluster_profile = "3"
```

## Archivos afectados

### medical_record (origen del cluster)
| Archivo | Cambio |
|---------|--------|
| `app/features/medical_record/domain/ports.py` | Nuevos ports `ISocialClusterPort`; `IMedicalRecordRepository.get_by_patient_id`; `IRiskPredictionRepository.get_latest_ok_for_medical_record` |
| `app/features/medical_record/application/evaluate_patient_risk_usecase.py` | Depende de `social_cluster_port`; propaga el cluster tras predicción `ok` |
| `app/features/medical_record/infrastructure/adapters/social_cluster_adapter.py` | **Nuevo.** Escribe el cluster en el perfil social vía `ForumsRepository` |
| `app/features/medical_record/infrastructure/repositories/medical_record_repository.py` | Nuevo `get_by_patient_id` |
| `app/features/medical_record/infrastructure/repositories/risk_prediction_repository.py` | Nuevo `get_latest_ok_for_medical_record` (última con `status="ok"`) |

### forums (consumo del cluster)
| Archivo | Cambio |
|---------|--------|
| `app/features/forums/domain/ports.py` | Nuevo `IPatientClusterLookup`; nuevos métodos en `IForumsRepository`: `update_cluster_profile`, `get_groups_by_cluster`, `get_feed_by_cluster` |
| `app/features/forums/domain/community_group_entity.py` | Nuevo campo `cluster_tag` |
| `app/features/forums/application/profiles/create_profile_usecase.py` | Depende de `cluster_lookup`; deriva el cluster, ignora el del cliente |
| `app/features/forums/application/posts/get_recommended_feed_usecase.py` | **Nuevo.** Feed por cluster con fallback a global |
| `app/features/forums/application/groups/get_recommended_groups_usecase.py` | **Nuevo.** Grupos por cluster con fallback a todos |
| `app/features/forums/infrastructure/adapters/patient_cluster_adapter.py` | **Nuevo.** Resuelve cluster: user → patient → expediente → predicción `ok` |
| `app/features/forums/infrastructure/repositories/forums_repository.py` | `update_cluster_profile`, `get_feed_by_cluster` (join a `social_profiles`), `get_groups_by_cluster` |
| `app/features/forums/infrastructure/models/community_group_model.py` | Nueva columna `cluster_tag` |
| `app/features/forums/infrastructure/controllers/*` , `routes/*` , `schemas/forums_schemas.py` | Endpoints `/posts/recommended` y `/groups/recommended` (JWT); `cluster_tag` en grupos; `cluster_profile` removido de `ProfileCreate` |
| `app/core/containers.py` | Wiring de adapters y usecases nuevos |

### Endpoints nuevos
- `GET /api/v1/forums/posts/recommended` — requiere JWT. Posts de autoras del mismo cluster; fallback global.
- `GET /api/v1/forums/groups/recommended` — requiere JWT. Grupos con `cluster_tag` del cluster; fallback a todos.
- `POST /api/v1/forums/groups` ahora acepta `cluster_tag` opcional.

## Privacidad

El cluster deriva de datos médicos, así que:
- Las respuestas de los endpoints **no exponen** el `cluster_profile` de otras autoras (`PostResponse` no incluye el campo).
- La recomendación es implícita ("Para ti"). **El front no debe rotular** la sección con el nombre del cluster de riesgo (p. ej. no mostrar "Grupos de riesgo metabólico").

## Migración de base de datos

`create_all` no altera tablas existentes. En bases ya desplegadas:

```sql
ALTER TABLE community_groups ADD COLUMN cluster_tag VARCHAR(50);
```

(`social_profiles.cluster_profile` ya existía.) En los tests, SQLite se crea desde cero, no requiere migración.

## Tests

- `tests/test_forums/test_cluster_recommendations.py` — usecases (con cluster / fallback).
- `tests/test_forums/test_forums_repository_cluster.py` — repos contra SQLite.
- `tests/test_forums/test_patient_cluster_adapter.py`, `tests/test_medical_record/test_social_cluster_adapter.py` — adapters.
- `tests/test_medical_record/test_evaluate_patient_risk_usecase.py` — propagación del cluster.
- `tests/test_forums_cluster_e2e.py` — flujo completo end to end (evaluación con ML mockeado → cluster en perfil → feed filtrado → fallback).
