# Resumen — Implementación de patrones ADR

Backend `salud_prenatal_backend` (FastAPI + SQLAlchemy, arquitectura hexagonal por feature).
Se implementaron los **8 patrones ADR pendientes** (3 parciales + 5 ausentes) **sin tocar la base de datos ni las rutas públicas**.

## Estado de las pruebas

| Métrica | Resultado |
|---|---|
| Tests totales | 196 |
| Pasan | 195 |
| Fallos reales de código | 0 |
| Fallos de entorno preexistentes | 1 (versión de Pydantic en el sandbox) |
| Snapshot de rutas (API pública) | VERDE (intacto) |
| Tests nuevos añadidos | +28 |

## Patrones implementados

### Parciales → completos

| ADR | Patrón | Qué se hizo |
|---|---|---|
| 03 | Protection Proxy | `ProtectedMedicalRecordRepository` implementa `IMedicalRecordRepository` y verifica la relación paciente-doctor antes de delegar. Se quitó el `if` inline del use case. |
| 05 | Notification | `app/core/notification.py` + `PatientDiaryValidator` con validación de rangos (systolic/diastolic/weight y diastolic<systolic), acumulando todos los errores. |
| 12 | Factory Method | `InvitationCodeFactory` (abstracto) + `UuidInvitationCodeFactory`; el repositorio delega la generación del código. |

### Ausentes → implementados

| ADR | Patrón | Qué se hizo |
|---|---|---|
| 04 | Observer | `app/core/events/` con `EventBus`, `DomainEvent`, eventos y `LoggingSubscriber`. Se publican desde `create_appointment` y `redeem_invitation_code`. Bus como Singleton. |
| 08 | Specification | `app/core/specification.py` (base con and/or/not) + specs `PatientExists`/`DoctorExists` en `create_appointment`. |
| 07 | Query Object | `NameSearchCriteria` encapsula el matching; los dos use cases de búsqueda delegan en él. |
| 13 | Composite | `ForumComponent`/`PostComposite`/`CommentLeaf` + `BuildPostThreadUseCase` (árbol post→comentarios). |
| 14 | Strategy | `ISymptomAnalysisStrategy` + `KeywordSymptomStrategy`/`NoopSymptomStrategy` + `SymptomAnalyzer` + `AnalyzeSymptomsUseCase`. |

## Notas importantes

- **Composite (13) y Strategy (14)** quedaron cableados en el container y con tests, pero **no expuestos como endpoints nuevos**, para no alterar el snapshot de rutas. Se pueden exponer bajo pedido (actualizando `EXPECTED_ROUTES` deliberadamente).
- **Sin dependencias nuevas**: todo usa stdlib + lo ya presente. No hace falta reinstalar `requirements.txt`.
- El único fallo (`test_user_response_accepts_legacy_short_fields`) es **preexistente** y por versión de Pydantic del entorno, no por estos cambios.

## Agente de pruebas

Se creó la definición de un subagente `tester` (solo lectura: corre pytest y reporta VERDE/ROJO, distingue fallos reales de los de entorno). Para activarlo, copiar `tester.md` a `.claude/agents/tester.md`.

## Cómo verificar

```
.venv\Scripts\python -m pytest          # suite completa (Windows)
.venv\Scripts\python -m pytest tests/test_smoke.py   # snapshot de rutas
```
