# ADR-01: Cifrado de Datos Sensibles

## Fecha

18/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio recolecta datos médicos e identificables extremadamente sensibles para la estimación de riesgos del embarazo. Según regulaciones internacionales y políticas de Google Play Store, es obligatorio cifrar esta información para proteger la confidencialidad de la paciente contra posibles filtraciones.

## Decisión

Implementar el patrón Data Mapper (Fowler) para separar el dominio de la persistencia e interceptar y cifrar los campos sensibles antes del almacenamiento físico.

## Consecuencias

### Pros

- Centraliza la seguridad en la persistencia, manteniendo el dominio libre de lógica criptográfica.

- Cumple estrictamente con las normativas legales de protección de datos clínicos del paciente.

### Contras

- Impide búsquedas parciales directas en base de datos, requiriendo indexación o descifrado previo.

- Incrementa ligeramente el uso de CPU debido a operaciones constantes de cifrado.

# ADR-02: Optimización de Consultas Históricas

## Fecha

18/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

Los médicos obstetras requieren consultar el historial completo de automonitoreo diario de la paciente para evaluar su evolución. Cargar todos los registros históricos de forma anticipada degradaría el rendimiento del servidor y aumentaría el consumo de ancho de banda.

## Decisión

Implementar el patrón Lazy Load (Fowler) para posponer la carga de los registros históricos del diario hasta que el médico los solicite explícitamente.

## Consecuencias

### Pros

- Reduce la memoria del servidor and el ancho de banda en consultas iniciales.

- Optimiza el tiempo de respuesta al abrir el perfil básico del paciente.

### Contras

- Puede generar múltiples llamadas consecutivas a la base de datos si no se optimiza.

- Incrementa la complejidad del mapeador al gestionar cargas diferidas en colecciones.

# ADR-03: Restricción de Acceso Clínico

## Fecha

18/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio exige salvaguardar la privacidad de la paciente, garantizando que su expediente solo sea consultado por su obstetra vinculado. Al cambiar de médico, se debe impedir que el nuevo profesional herede el historial clínico del médico anterior.

## Decisión

Implementar el patrón Protection Proxy (GoF) para interceptar consultas y validar que el médico tenga una vinculación activa autorizada con la paciente.

## Consecuencias

### Pros

- Asegura un control de acceso riguroso y transparente a nivel de dominio.

- Evita fugas de información clínica entre diferentes médicos de la plataforma.

### Contras

- Introduce una capa intermedia que añade complejidad a las pruebas de unidad.

- Requiere duplicar datos demográficos básicos al crear expedientes aislados por vinculación.

# ADR-04: Desacoplamiento de Notificaciones

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere enviar notificaciones automáticas ante diversos eventos: cambios de vinculación, citas agendadas y nuevos mensajes de chat. Acoplar el envío de notificaciones dentro de los servicios principales dificulta añadir nuevos canales de entrega.

Tras la migración a microservicios (ADR de split de servicios), `AppointmentCreatedEvent` y `MessageSentEvent` se publican y consumen dentro del mismo proceso (`service_transaccional`), donde viven todos los observers reales (log en tabla, WebSocket de chat, push Firebase). `PatientLinkedEvent`, en cambio, nace en `service_usuarios` (al redimir un código de invitación) — un proceso distinto, con su propio `InMemoryEventDispatcher` en memoria, aislado del de transaccional.

## Decisión

Implementar el patrón Observer (GoF) para tratar los servicios principales como sujetos observables y notificar eventos de estado a los despachadores de notificaciones.

Cada servicio mantiene su propio `InMemoryEventDispatcher` in-process (no hay bus de eventos compartido entre procesos). Para `PatientLinkedEvent`, cuyo origen (`service_usuarios`) no coincide con dónde viven los observers reales (`service_transaccional`), `service_usuarios` notifica el evento vía una llamada HTTP server-to-server a un endpoint interno de transaccional (`POST /notifications/internal/patient-linked`), que ahí sí lo publica en su propio dispatcher y llega a `NotificationLogObserver` y `FirebasePushObserver`. Ese endpoint está protegido por un secreto compartido (`INTERNAL_SERVICE_TOKEN`) — no basta con "vive en la red del compose", porque el catch-all de Traefik para transaccional expone `/api/v1` completo con `jwt-auth` (anónimo permitido), así que cualquier ruta nueva bajo ese prefijo es alcanzable públicamente si no se protege explícitamente. Se descartó definir el `NotificationModel`/observer de notificaciones en `shared_core` para que ambos servicios "compartieran" el dispatcher: eso duplicaba el modelo ORM de una tabla que no es dueño de `service_usuarios`, violando la regla de ownership de tablas del proyecto (dueño único vía `create_all`, los demás leen por read-model).

## Consecuencias

### Pros

- Desacopla la lógica de negocio de los mecanismos de entrega de notificaciones.

- Permite añadir nuevos canales de notificación sin modificar los servicios existentes.

- El flujo de vinculación de paciente ahora dispara notificación en tabla y push Firebase igual que citas/chat (antes del fix, el push de vinculación era código muerto: estaba suscrito en transaccional pero el evento nunca llegaba desde otro proceso).

### Contras

- El flujo reactivo dificulta el seguimiento de errores si falla la entrega.

- Requiere un despachador de eventos que incrementa la complejidad del sistema.

- Cruzar de `service_usuarios` a `service_transaccional` para `PatientLinkedEvent` exige una llamada HTTP adicional (best-effort, con timeout corto) en vez de una publicación in-process; si transaccional está caído, la notificación de vinculación se pierde silenciosamente (no bloquea la vinculación, que es la operación de negocio real).

# ADR-05: Validación de Datos Entrada

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El sistema debe garantizar la integridad física de las mediciones clínicas capturadas en el automonitoreo diario. Si múltiples mediciones son incorrectas, el sistema debe validar todos los campos y reportar de forma unificada los errores del formulario.

## Decisión

Implementar el patrón Notification (Fowler) para acumular todos los errores de validación física en un objeto antes de rechazar y retornar la solicitud.

## Consecuencias

### Pros

- Permite a la paciente conocer y corregir todos los errores en un viaje.

- Evita estados inconsistentes o físicamente imposibles en la base de datos.

### Contras

- Obliga a procesar todas las validaciones incluso si la primera ya falló.

- Requiere estructurar un objeto de notificación adicional en toda la API.

## Nota de implementación (as-built, 2026-07-20)

Implementado en `service_transaccional/app/patient_diaries`:
- `Notification` (patrón genérico, acumula errores sin abortar en el primero): [`domain/notification.py`](../service_transaccional/app/patient_diaries/domain/notification.py).
- `validate_diary_measurements(entity)` (reglas físicas: peso 20–300 kg, sistólica 40–300 mmHg, diastólica 20–200 mmHg, sistólica > diastólica) + excepción `PatientDiaryValidationError`: [`domain/diary_validation.py`](../service_transaccional/app/patient_diaries/domain/diary_validation.py). Campos `None` se saltan (soporta updates parciales).
- Enganchado en `CreatePatientDiaryUseCase` y `UpdatePatientDiaryUseCase` antes de persistir.
- `PatientDiaryController` mapea `PatientDiaryValidationError` → `HTTPException 422` con la lista completa de errores (antes cualquier excepción caía en el 500 genérico de `internal_error`).
- Tests: `test_patient_diary_notification.py`, `test_patient_diary_measurement_validation.py`, `test_create_patient_diary_usecase_validation.py`, `test_update_patient_diary_usecase_validation.py`, `test_patient_diary_controller_validation.py`.

# ADR-06: Integración del Servicio Inferencia

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio necesita clasificar el riesgo del embarazo usando un microservicio externo de Machine Learning. Esta llamada introduce latencia de red y posibles fallos que pueden afectar el tiempo de respuesta del servidor backend principal.

## Decisión

Implementar el patrón Gateway (Fowler) para encapsular la comunicación con el microservicio externo, administrando los payloads, reintentos y timeouts del servicio.

## Consecuencias

### Pros

- Aísla la integración de red del modelo de dominio de la aplicación.

- Facilita la implementación de políticas de resiliencia y fallbacks locales.

### Contras

- Requiere mantener una interfaz intermedia acoplada al contrato del servicio externo.

- Añade latencia adicional al realizar llamadas a través de la red.

## Nota de implementación (as-built, 2026-07-20)

Además de `MlPredictionServiceAdapter` (RF-32/33, clasificación de riesgo), el patrón Gateway también cubre `NlpSymptomAdapter` ([`service_transaccional/app/patient_diaries/infrastructure/adapters/nlp_symptom_adapter.py`](../service_transaccional/app/patient_diaries/infrastructure/adapters/nlp_symptom_adapter.py)) — encapsula la llamada HTTP al endpoint `/nlp/extract-symptoms-llm` del microservicio ML (RF-29, RF-31). Se reclasificó de ADR-14/Strategy: hoy es una única implementación concreta detrás de `ISymptomExtractionPort`, arquitectónicamente un Gateway (aísla la red, maneja timeout/fallback), no un Strategy con algoritmos intercambiables. Ver nota as-built en ADR-14 para el detalle de esa reclasificación y el candidato de Strategy real (checkout de pagos).

# ADR-07: Búsquedas Dinámicas en Directorio

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere que los médicos busquen y filtren dinámicamente pacientes según nombre, residencia y nivel de riesgo. Escribir estas consultas condicionales en los repositorios tradicionales de datos duplica el código y dificulta la mantenibilidad.

## Decisión

Implementar el patrón Query Object (Fowler) para representar los filtros del directorio como objetos de consulta que traducen condicionales a sentencias SQL.

## Consecuencias

### Pros

- Aísla la sintaxis de base de datos de las reglas de filtrado.

- Facilita la reutilización y composición de filtros en múltiples endpoints.

### Contras

- Exige diseñar una abstracción de consultas personalizada en lugar de directo.

- Incrementa la cantidad de clases necesarias para dar soporte a búsquedas.

## Nota de implementación (estado real, actualizado post-split a microservicios)

Estado: **parcialmente aplicable**. La búsqueda por nombre (RF-14) está implementada en `SearchPatientsByNameUseCase` y `SearchMedicalRecordsByPatientNameUseCase`, pero el filtrado ocurre **en memoria (Python)**, no como Query Object traducido a SQL.

Motivo: los campos `name`/`last_name` están cifrados con `EncryptedString` (Fernet, ADR-01), que es **no determinista** — el mismo texto produce ciphertext distinto en cada fila. Por eso es imposible filtrar por nombre con `WHERE ... LIKE` sobre la columna cifrada; hay que descifrar y comparar en memoria. Se acota primero a los pacientes del médico (`get_patients_by_doctor`) para limitar el conjunto. Es exactamente la contra documentada del ADR-01.

**Corrección (2026-07-20):** de los 3 filtros que pide RF-15, solo **uno** sigue siendo viable para Query Object hoy:

- **Residencia** — `medical_records.residence` es ahora **también `EncryptedString`** (`service_transaccional/app/medical_record/infrastructure/models/medical_record_model.py`). Mismo problema que el nombre: no se puede traducir a `WHERE ... LIKE` en SQL. Antes de este corte se documentó como "texto plano" — eso ya no es cierto tras el split, hay que descifrar y comparar en memoria igual que el nombre.
- **Nivel de riesgo / cluster** — `social_profiles.cluster_profile` (`String(50)`, `service_transaccional/app/forums/infrastructure/models/social_profile_model.py`) sigue **en texto plano**. Es el único candidato real hoy para Query Object — de hecho la técnica SQL ya se usa ahí mismo (`get_groups_by_cluster`, `get_feed_by_cluster` en `forums_repository.py`), solo falta exponerla como filtro del directorio de pacientes.
- **Fecha de vinculación** — no existe columna en `Patient` (`service_usuarios/app/users/infrastructure/models/patient_model.py`) que registre cuándo se vinculó al doctor; solo hay `doctor_id` (FK plano, filtrable, pero sin fecha). Requiere agregar la columna antes de poder filtrar por este criterio.

Alternativa futura para habilitar búsqueda por nombre/residencia en SQL: **índice ciego (blind index)** — una columna hash determinista (HMAC del valor normalizado) poblada al escribir y consultada por SQL, sin exponer el texto plano. Con el cifrado ahora cubriendo también residencia, esta alternativa gana relevancia si se quiere Query Object real sobre esos dos campos.

## Implementación (as-built, 2026-07-20) — filtro por nivel de riesgo + fecha de vinculación

Se implementó el Query Object real para los dos criterios que sí son SQL-puro hoy (cluster y `linked_at`); residencia queda pendiente (requiere blind index, fuera de este alcance):

- `PatientDirectoryQuery` (dataclass, `doctor_id` + `patient_ids_filter` opcional + `linked_after`/`linked_before`): [`service_usuarios/app/users/domain/patient_directory_query.py`](../service_usuarios/app/users/domain/patient_directory_query.py).
- `PatientRepository.search_directory(query)`: [`service_usuarios/app/users/infrastructure/repositories/patient_repository.py`](../service_usuarios/app/users/infrastructure/repositories/patient_repository.py) — el Query Object SQL de verdad (`WHERE doctor_id = ? AND patient_id IN (...) AND linked_at BETWEEN ?`).
- `Patient.linked_at` (columna nueva, se fija en `update_doctor` al vincular y se limpia al desvincular).
- `IPatientClinicalFilterPort.get_patient_ids_by_risk_cluster(doctor_id, risk_cluster)` + `RiskClusterFilterAdapter`: [`.../infrastructure/adapters/risk_cluster_filter_adapter.py`](../service_usuarios/app/users/infrastructure/adapters/risk_cluster_filter_adapter.py) — lee `social_profiles.cluster_profile` (read-model `SocialProfileRead`) por ser la única fuente plana; **no** `risk_predictions.prediction` (JSON, requeriría parseo en memoria). Caveat: un paciente sin perfil social (nunca entró al foro) no tiene fila en `social_profiles` y por tanto nunca aparece en este filtro, aunque sí tenga una predicción de riesgo vigente.
- `SearchPatientDirectoryUseCase` orquesta: si viene `risk_cluster`, resuelve `patient_ids` vía el port (corta temprano devolviendo `[]` si no hay coincidencias, sin tocar el repositorio) y arma el `PatientDirectoryQuery`.
- Ruta: `GET /api/v1/doctors/{doctor_id}/patients/directory?risk_cluster=&linked_after=&linked_before=`.
- Tests: `service_usuarios/tests/{test_patient_directory_query.py, test_risk_cluster_filter_adapter.py, test_search_patient_directory_usecase.py, test_patient_repository_linked_at.py, test_patient_directory_e2e.py}`.

# ADR-08: Gestión de Agenda Citas

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio exige validar que el médico tenga disponibilidad horaria y vinculación activa con la paciente antes de registrar una cita. Mezclar estas reglas comerciales con el flujo de almacenamiento dificulta modificar las políticas de agenda del consultorio.

## Decisión

Implementar el patrón Specification (Fowler) para encapsular las políticas de disponibilidad y vinculación en objetos de reglas independientes que se evalúan dinámicamente.

## Consecuencias

### Pros

- Facilita modificar las reglas de agendamiento sin tocar el servicio principal.

- Permite reutilizar las mismas reglas de validación en diferentes endpoints.

### Contras

- Añade indirección y complejidad al separar la validación del flujo principal.

- Requiere definir clases adicionales para cada regla o combinación lógica.

## Nota de implementación (as-built, 2026-07-20)

Implementado en `service_transaccional`:
- `IAppointmentSpecification` + `DoctorAvailabilitySpecification` + `ActivePatientLinkSpecification`: [`app/appointments/domain/specifications.py`](../service_transaccional/app/appointments/domain/specifications.py).
- `CreateAppointmentUseCase` recibe `specifications: List[IAppointmentSpecification]` (opcional, default `[]`) y acumula todos los `error_message()` de las specs no satisfechas en un único `ValueError` antes de persistir.
- Wiring en `service_transaccional/container.py`: `providers.List(doctor_availability_specification, active_patient_link_specification)` inyectado en `create_appointment_use_case`.
- Tests: `service_transaccional/tests/test_appointment_specifications.py` (specs aisladas) y `test_create_appointment_usecase_specifications.py` (enforcement en el caso de uso).

# ADR-09: Ruteo del Chat WebSocket

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere un chat en tiempo real entre pacientes y recepción, verificando la autenticación JWT. Conectar a los usuarios de forma directa colapsaría el sistema de red y dificultaría la persistencia centralizada de las conversaciones.

## Decisión

Implementar el patrón Mediator (GoF) mediante un manager central que autentica conexiones, administra sockets activos, persiste mensajes y los enruta al destinatario.

## Consecuencias

### Pros

- Centraliza el control de conexiones activas, autenticación JWT y auditoría.

- Evita que los clientes de chat tengan que conocerse directamente.

### Contras

- El mediador centralizado constituye un punto único de falla del sistema.

- Puede congestionarse bajo un volumen extremo de tráfico de mensajes simultáneos.

# ADR-10: Lógica Cuentas de Usuarios

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El sistema maneja múltiples roles (médicos, pacientes, recepcionistas) con procesos específicos de registro, activación y visualización de cuentas. Escribir estas reglas comerciales en la capa de persistencia mezcla responsabilidades y vulnera el control de acceso.

## Decisión

Implementar el patrón Service Layer (Fowler) para encapsular la lógica de creación, activación y consulta de cuentas de usuario en servicios independientes del controlador.

## Consecuencias

### Pros

- Define una frontera clara de servicios disponibles para los clientes web.

- Centraliza las transacciones de negocio facilitando el mantenimiento y pruebas.

### Contras

- Añade una capa de código adicional que puede resultar redundante inicialmente.

- Exige mapear datos entre capas incrementando ligeramente la sobrecarga de desarrollo.

# ADR-11: Autenticación Segura con JWT

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere verificar la identidad de los usuarios mediante tokens JWT en cada petición REST y WebSocket. Distribuir la verificación del token en cada servicio del backend incrementa el riesgo de vulnerabilidades de seguridad por descuido.

## Decisión

Implementar el patrón Remote Facade (Fowler) para centralizar la autenticación, validación de JWT y extracción de identidad en un componente único de interceptación de entrada.

## Consecuencias

### Pros

- Agrupa y centraliza la lógica de validación de seguridad para toda la aplicación.

- Evita duplicación de código de validación de tokens en los controladores.

### Contras

- Introduce una dependencia obligatoria en la cabecera de todas las peticiones.

- Puede convertirse en un cuello de botella para el rendimiento general.

## Nota de implementación (estado real en Microservicios)

Estado: **Implementado y evolucionado a ForwardAuth Edge**. 
En la arquitectura de vertical slicing (`service_auth`, `service_gateway`, `service_usuarios`, `service_pagos`, `service_transaccional`), el patrón evoluciona a un esquema donde **Traefik (edge proxy)** consulta al **API Gateway (`service_gateway`)** mediante **ForwardAuth** (`/validate` y `/validate/strict`).

El API Gateway es el único componente que decodifica el JWT (usando `IJwtKeyProvider` de `shared_core`, respaldado por Vault o variables de entorno). Una vez validada la firma, Traefik inyecta las cabeceras `X-User-Id`, `X-User-Email`, `X-User-Role`, `X-Subscription-Status` en la petición entrante hacia los microservicios de dominio. Ningún microservicio de dominio valida JWTs directamente.


# ADR-12: Generación Código de Vinculación

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere generar códigos alfanuméricos de vinculación que expiren y sean de un solo uso. La lógica para generar, firmar y estructurar el formato de estos códigos debe estar separada de los controladores de usuarios.

## Decisión

Implementar el patrón Factory Method (GoF) para delegar la creación y formato del código de vinculación en un generador especializado de tokens clínicos.

## Consecuencias

### Pros

- Aísla la lógica de generación y firma del código del resto del sistema.

- Facilita cambiar el formato de los códigos (QR o alfanumérico) sin modificar clientes.

### Contras

- Requiere crear subclases o fábricas específicas que complican el diseño de clases.

- Incrementa la indirección al crear códigos de vinculación sencillos del sistema.

# ADR-13: Estructura del Foro Comunitario

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere que las pacientes publiquen experiencias, creen grupos de apoyo temáticos y comenten publicaciones. Administrar este árbol jerárquico de publicaciones y comentarios de forma separada acopla el sistema y complica su representación.

## Decisión

Implementar el patrón de diseño Composite (GoF) para tratar de forma uniforme las publicaciones individuales y los hilos de conversación jerárquicos del foro.

## Consecuencias

### Pros

- Simplifica el cliente al permitir tratar publicaciones simples e hilos de comentarios idénticamente.

- Facilita la incorporación de nuevas categorías o grupos de discusión en el foro.

### Contras

- Dificulta restringir operaciones específicas en ciertos nodos del árbol sin añadir lógica adicional.

- Complica el diseño del esquema de base de datos para mapear jerarquías recursivas.

# ADR-14: Procesamiento de Lenguaje Natural

## Fecha

24/06/2026

## Estado

Suggested

## Responsables

Maximiliano Diaz

## Contexto

El negocio requiere procesar síntomas e inquietudes clínicas en texto libre ingresados por las pacientes mediante técnicas de procesamiento de lenguaje natural. Esto permite identificar automáticamente anomalías médicas complejas que no se reportan numéricamente.

## Decisión

Implementar el patrón Strategy (GoF) para definir e intercambiar dinámicamente diferentes algoritmos de extracción y procesamiento de lenguaje natural de los síntomas clínicos.

## Consecuencias

### Pros

- Permite evaluar e intercambiar motores de análisis de texto sin afectar la persistencia.

- Encapsula cada algoritmo de procesamiento de lenguaje natural de forma totalmente aislada.

### Contras

- El backend debe manejar múltiples estrategias aumentando la complejidad del mantenimiento de algoritmos.

- Requiere mapear diferentes formatos de salida de los distintos proveedores de análisis de texto.

## Nota de implementación (as-built, 2026-07-20)

**Implementación canónica — `service_pagos` (checkout de suscripciones):**

- `ICheckoutStrategy` (puerto): [`domain/ports.py`](../service_pagos/app/subscriptions/domain/ports.py) — `create_checkout_session(user_id, email, plan_type, stripe_customer_id)`.
- **2 estrategias concretas** en [`infrastructure/adapters/stripe_checkout_strategies.py`](../service_pagos/app/subscriptions/infrastructure/adapters/stripe_checkout_strategies.py):
  - `StripeRecurringCheckoutStrategy` — modo `subscription`, precios recurrentes.
  - `StripeOneTimeCheckoutStrategy` — modo `payment`, acepta `card`/`oxxo`/`customer_balance` (SPEI), crea customer explícito.
- **Selección en runtime por parámetro de negocio**: `CreateCheckoutSessionUseCase` ([`application/create_checkout_session_usecase.py`](../service_pagos/app/subscriptions/application/create_checkout_session_usecase.py)) recibe `checkout_strategies: Dict[PaymentModeEnum, ICheckoutStrategy]` y elige con `self.checkout_strategies.get(payment_mode)`.
- Wiring en `service_pagos/container.py`: `providers.Dict({PaymentModeEnum.recurring: ..., PaymentModeEnum.one_time: ...})`.
- Trazabilidad: RF-42.

Este es el ejemplo fiel del patrón: mismo contrato, algoritmos intercambiables, elegidos dinámicamente por un parámetro de negocio — no hardcodeado.

**Implementación previa — NLP (`service_transaccional`), estado: parcial.**

`ISymptomExtractionPort` ([`patient_diaries/domain/ports.py`](../service_transaccional/app/patient_diaries/domain/ports.py)) tiene **una sola implementación concreta** (`NlpSymptomAdapter`, HTTP al microservicio ML `/nlp/extract-symptoms-llm`). Sin una segunda estrategia intercambiable, esto es arquitectónicamente un **Gateway** (mismo rol que ADR-06), no un Strategy realizado — el propio código se autodocumenta así ("patron Gateway - ADR-06/14"). Queda como candidato futuro: si se conserva una implementación alterna (p. ej. un motor ONNX local además del LLM actual), seleccionable por config (`NLP_ENGINE=onnx|llm`), ahí sí se completaría un segundo caso real de Strategy.
