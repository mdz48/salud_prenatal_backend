# Documento de Requerimientos del Proyecto: Salud Prenatal

Este documento detalla y estructura los requerimientos del software **Salud Prenatal**, presentados en listas numeradas consecutivas para facilitar su conteo y trazabilidad.

---

## 1. Matriz de Requerimientos Funcionales (RF)

A continuación se presentan los cuarenta (40) requerimientos funcionales del sistema (activos y planeados para el futuro), habiendo eliminado los requerimientos descartados u obsoletos.

| ID REQ | Descripción del Requerimiento | Módulo | Estado de Implementación |
|--------|-------------------------------|--------|--------------------------|
| **RF-01** | El sistema debe permitir el registro de cuentas de médicos ginecólogos/obstetras con sus datos personales y profesionales. | Autenticación y Usuarios | **`[Activo - Implementado]`** |
| **RF-02** | El sistema debe permitir el registro de cuentas de pacientes embarazadas con sus datos personales y clínicos. | Autenticación y Usuarios | **`[Activo - Implementado]`** |
| **RF-03** | El sistema debe permitir el registro de cuentas de recepcionistas asociadas a un consultorio médico. | Autenticación y Usuarios | **`[Activo - Implementado]`** |
| **RF-04** | El sistema debe encriptar las contraseñas de todos los usuarios de forma irreversible para garantizar la seguridad. | Autenticación y Usuarios | **`[Activo - Implementado]`** |
| **RF-05** | El sistema debe autenticar usuarios mediante inicio de sesión con tokens JWT. | Autenticación y Usuarios | **`[Activo - Implementado]`** |
| **RF-06** | El sistema debe permitir al administrador activar o desactivar cuentas de médicos y recepcionistas. | Autenticación y Usuarios | **`[Activo - Pendiente]`** |
| **RF-07** | El sistema debe generar un código único de vinculación (QR o alfanumérico) por cada paciente vinculado a un médico. | Vinculación | **`[Activo - Implementado]`** |
| **RF-08** | El sistema debe permitir al paciente escanear o ingresar el código para vincularse a su médico tratante. | Vinculación | **`[Activo - Implementado]`** |
| **RF-09** | El sistema debe confirmar la vinculación exitosa entre la cuenta del paciente y la del médico. | Vinculación | **`[Activo - Implementado]`** |
| **RF-10** | El sistema debe notificar al médico y al paciente sobre el estado de la vinculación. | Vinculación | **`[Activo - Pendiente]`** |
| **RF-11** | El sistema debe gestionar la expiración y reutilización de códigos de vinculación. | Vinculación | **`[Activo - Implementado]`** |
| **RF-12** | El sistema debe impedir que un paciente transfiera su expediente a otro médico (debe iniciar desde cero). | Vinculación | **`[Activo - Pendiente]`** |
| **RF-13** | El sistema debe mostrar al médico el directorio completo de todos sus pacientes vinculados. | Directorio | **`[Activo - Implementado]`** |
| **RF-14** | El sistema debe permitir al médico buscar pacientes por nombre o identificador dentro de su directorio. | Directorio | **`[Activo - Pendiente]`** |
| **RF-15** | El sistema debe permitir al médico filtrar pacientes según criterios disponibles (fecha de vinculación, nivel de riesgo, etc.). | Directorio | **`[Activo - Pendiente]`** |
| **RF-16** | El sistema debe permitir al médico acceder al perfil individual completo de una paciente. | Directorio | **`[Activo - Implementado]`** |
| **RF-17** | El sistema debe permitir al paciente registrar su presión arterial de forma diaria. | Automonitoreo | **`[Activo - Implementado]`** |
| **RF-18** | El sistema debe permitir al paciente registrar su peso corporal de forma diaria. | Automonitoreo | **`[Activo - Implementado]`** |
| **RF-19** | El sistema debe permitir al paciente registrar síntomas e inquietudes en texto libre. | Automonitoreo | **`[Activo - Implementado]`** |
| **RF-20** | El sistema debe validar que los datos capturados (presión arterial y peso) estén en rangos y formatos correctos. | Automonitoreo | **`[Activo - Pendiente]`** |
| **RF-21** | El sistema debe almacenar el historial completo de automonitoreo de cada paciente. | Automonitoreo | **`[Activo - Implementado]`** |
| **RF-22** | El sistema debe permitir al médico consultar los registros históricos de presión y peso de una paciente. | Automonitoreo | **`[Activo - Implementado]`** |
| **RF-23** | El sistema debe permitir al recepcionista crear citas entre pacientes y médicos según elección previa de la paciente. | Citas y Agenda | **`[Activo - Implementado]`** |
| **RF-24** | El sistema debe verificar la disponibilidad del médico en la fecha y hora seleccionadas para la cita. | Citas y Agenda | **`[Activo - Pendiente]`** |
| **RF-25** | El sistema debe permitir al recepcionista cancelar citas programadas. | Citas y Agenda | **`[Activo - Implementado]`** |
| **RF-26** | El sistema debe notificar a los médicos sobre citas pendientes o próximas. | Citas y Agenda | **`[Activo - Pendiente]`** |
| **RF-27** | El sistema debe permitir al paciente consultar sus próximas citas programadas. | Citas y Agenda | **`[Activo - Implementado]`** |
| **RF-28** | El sistema debe permitir al paciente y al médico consultar el historial de citas. | Citas y Agenda | **`[Activo - Implementado]`** |
| **RF-29** | El sistema debe procesar los síntomas registrados por las pacientes en texto libre mediante técnicas de NLP (Procesamiento de Lenguaje Natural). | Análisis (NLP) | **`[Futuro - Planeado]`** |
| **RF-30** | El sistema debe generar un resumen clínico automatizado del estado reciente de cada paciente utilizando NLP. | Análisis (NLP) | **`[Futuro - Planeado]`** |
| **RF-31** | El sistema debe identificar síntomas recurrentes y extraer entidades clínicas relevantes del texto libre de la paciente. | Análisis (NLP) | **`[Futuro - Planeado]`** |
| **RF-32** | El sistema debe clasificar a la paciente en uno de cuatro perfiles de riesgo (Primigestas Sanas, Alto Riesgo Hipertensivo, Multíparas Sanas, Riesgo Metabólico/Obesidad) utilizando un modelo de Machine Learning de clustering (KNN y PCA). | Análisis (ML) | **`[Activo - Implementado]`** |
| **RF-33** | El sistema debe mostrar al médico la clasificación de riesgo obtenida como apoyo para la toma de decisiones clínicas. | Análisis (ML) | **`[Activo - Implementado]`** |
| **RF-34** | El sistema debe permitir el envío y recepción de mensajes entre pacientes y recepcionistas. | Mensajería | **`[Activo - Implementado]`** |
| **RF-35** | El sistema debe mostrar el historial completo de conversaciones entre un paciente y el recepcionista. | Mensajería | **`[Activo - Implementado]`** |
| **RF-36** | El sistema debe generar notificaciones para nuevos mensajes no leídos. | Mensajería | **`[Activo - Pendiente]`** |
| **RF-37** | El sistema debe permitir a las pacientes publicar experiencias e inquietudes en un foro comunitario. | Comunidad (Foros) | **`[Futuro - Planeado]`** |
| **RF-38** | El sistema debe permitir la creación y gestión de grupos de apoyo temáticos dentro del foro de la comunidad. | Comunidad (Foros) | **`[Futuro - Planeado]`** |
| **RF-39** | El sistema debe permitir a las pacientes comentar e interactuar en las publicaciones de otras usuarias del foro. | Comunidad (Foros) | **`[Futuro - Planeado]`** |
| **RF-40** | El sistema debe permitir a los médicos publicar artículos y consejos de salud en la sección de comunidad. | Comunidad (Foros) | **`[Futuro - Planeado]`** |

---

## 2. Requerimientos Técnicos y de Sistema Activos (RT)

- **RT-1 Generación de Códigos Únicos:** El sistema debe generar códigos QR y alfanuméricos únicos y seguros para la vinculación de cuentas.
- **RT-2 Expiración de Códigos:** El sistema debe gestionar la expiración temporal y la política de un solo uso de los códigos de vinculación generados.
- **RT-3 Restricción de Acceso (Expedientes):** El backend debe validar que el médico que intenta consultar un perfil o expediente clínico tenga una relación de vinculación activa con esa paciente en la base de datos.
- **RT-4 Validación de Rangos Biológicos:** El sistema debe validar que los datos clínicos capturados por la paciente en su diario (presión arterial y peso) se encuentren en rangos biológicos coherentes antes de ser registrados en la base de datos.
- **RT-5 Almacenamiento Histórico:** El sistema debe almacenar registros de automonitoreo garantizando su orden cronológico y trazabilidad temporal inmutable.
- **RT-6 Asociación de Registros:** El backend debe asociar inequívocamente cada entrada de diario clínico y monitoreo a la paciente correspondiente.
- **RT-7 Validación de Vinculación en Citas:** El sistema debe comprobar que la paciente tenga una vinculación activa con el médico obstetra antes de permitir que la recepcionista agende la cita.
- **RT-8 Control de Disponibilidad (No Duplicidad):** El sistema debe verificar la disponibilidad del médico obstetra en la fecha y hora solicitadas para impedir el registro de dos citas en la misma hora.
- **RT-9 Inferencia de Nivel de Riesgo (On-the-fly):** El sistema debe recopilar las variables clínicas del historial y ejecutar solicitudes HTTP al microservicio de Machine Learning para obtener la clusterización en las 4 categorías (Primigestas Sanas, Alto Riesgo Hipertensivo, Multíparas Sanas, Riesgo Metabólico) mediante KNN.
- **RT-10 Módulo de Mensajería Interna:** El backend debe mantener conexiones WebSocket activas, resolver las consultas del historial de conversaciones de forma indexada y despachar notificaciones inmediatas de nuevos mensajes.

---

## 3. Requerimientos No Funcionales (RNF)

- **RNF-1 Cifrado en Tránsito:** Toda transferencia de datos (llamadas REST HTTP y canales de chat WebSockets) debe ocurrir bajo cifrado SSL/TLS (HTTPS y WSS).
- **RNF-2 Validación JWT en Sockets:** La conexión al servidor de WebSockets debe requerir y validar de manera estricta el token JWT del usuario emisor en el inicio de la conexión.
- **RNF-3 Desacoplamiento de Servicios de IA:** Los procesos de inferencia del modelo de Machine Learning deben ejecutarse de forma independiente a la base de datos principal, en un microservicio de Python separado.

---

## 4. Requerimientos Técnicos en Backlog (Futuras Fases)

- **RT-F1 Integración de base de datos de foros:** Diseñar e implementar el modelo relacional para publicaciones, comentarios e interacciones de la futura sección de comunidad.
- **RT-F2 Procesamiento NLP asíncrono:** Implementar un worker en segundo plano para procesar textos libres de las pacientes y extraer métricas sin bloquear la API principal.
