# Matriz de Trazabilidad: Requerimientos vs. ADRs

Esta tabla vincula cada uno de los cuarenta (40) requerimientos funcionales del sistema con su decisión arquitectónica (ADR) correspondiente, respaldada por un patrón de diseño GoF o Fowler.

| ID REQ | Descripción del Requerimiento | ADR Asignado | Patrón de Diseño |
|--------|-------------------------------|--------------|------------------|
| **RF-01** | El sistema debe permitir el registro de cuentas de médicos ginecólogos/obstetras con sus datos personales y profesionales. | **ADR-10** | Service Layer (Fowler) |
| **RF-02** | El sistema debe permitir el registro de cuentas de pacientes embarazadas con sus datos personales y clínicos. | **ADR-10** | Service Layer (Fowler) |
| **RF-03** | El sistema debe permitir el registro de cuentas de recepcionistas asociadas a un consultorio médico. | **ADR-10** | Service Layer (Fowler) |
| **RF-04** | El sistema debe encriptar las contraseñas de todos los usuarios de forma irreversible para garantizar la seguridad. | **ADR-01** | Data Mapper (Fowler) |
| **RF-05** | El sistema debe autenticar usuarios mediante inicio de sesión con tokens JWT. | **ADR-11** | Remote Facade (Fowler) |
| **RF-06** | El sistema debe permitir al administrador activar o desactivar cuentas de médicos y recepcionistas. | **ADR-10** | Service Layer (Fowler) |
| **RF-07** | El sistema debe generar un código único de vinculación (QR o alfanumérico) por cada paciente vinculado a un médico. | **ADR-12** | Factory Method (GoF) |
| **RF-08** | El sistema debe permitir al paciente escanear o ingresar el código para vincularse a su médico tratante. | **ADR-12** | Factory Method (GoF) |
| **RF-09** | El sistema debe confirmar la vinculación exitosa entre la cuenta del paciente y la del médico. | **ADR-12** | Factory Method (GoF) |
| **RF-10** | El sistema debe notificar al médico y al paciente sobre el estado de la vinculación. | **ADR-04** | Observer (GoF) |
| **RF-11** | El sistema debe gestionar la expiración y reutilización de códigos de vinculación. | **ADR-12** | Factory Method (GoF) |
| **RF-12** | El sistema debe impedir que un paciente transfiera su expediente a otro médico (debe iniciar desde cero). | **ADR-03** | Protection Proxy (GoF) |
| **RF-13** | El sistema debe mostrar al médico el directorio completo de todos sus pacientes vinculados. | **ADR-07** | Query Object (Fowler) |
| **RF-14** | El sistema debe permitir al médico buscar pacientes por nombre o identificador dentro de su directorio. | **ADR-07** | Query Object (Fowler) |
| **RF-15** | El sistema debe permitir al médico filtrar pacientes según criterios disponibles (fecha de vinculación, nivel de riesgo, etc.). | **ADR-07** | Query Object (Fowler) |
| **RF-16** | El sistema debe permitir al médico acceder al perfil individual completo de una paciente. | **ADR-03** | Protection Proxy (GoF) |
| **RF-17** | El sistema debe permitir al paciente registrar su presión arterial de forma diaria. | **ADR-05** | Notification (Fowler) |
| **RF-18** | El sistema debe permitir al paciente registrar su peso corporal de forma diaria. | **ADR-05** | Notification (Fowler) |
| **RF-19** | El sistema debe permitir al paciente registrar síntomas e inquietudes en texto libre. | **ADR-05** | Notification (Fowler) |
| **RF-20** | El sistema debe validar que los datos capturados (presión arterial y peso) estén en rangos y formatos correctos. | **ADR-05** | Notification (Fowler) |
| **RF-21** | El sistema debe almacenar el historial completo de automonitoreo de cada paciente. | **ADR-01** | Data Mapper (Fowler) |
| **RF-22** | El sistema debe permitir al médico consultar los registros históricos de presión y peso de una paciente. | **ADR-02** | Lazy Load (Fowler) |
| **RF-23** | El sistema debe permitir al recepcionista crear citas entre pacientes y médicos según elección previa de la paciente. | **ADR-08** | Specification (Fowler) |
| **RF-24** | El sistema debe verificar la disponibilidad del médico en la fecha y hora seleccionadas para la cita. | **ADR-08** | Specification (Fowler) |
| **RF-25** | El sistema debe permitir al recepcionista cancelar citas programadas. | **ADR-08** | Specification (Fowler) |
| **RF-26** | El sistema debe notificar a los médicos sobre citas pendientes o próximas. | **ADR-04** | Observer (GoF) |
| **RF-27** | El sistema debe permitir al paciente consultar sus próximas citas programadas. | **ADR-08** | Specification (Fowler) |
| **RF-28** | El sistema debe permitir al paciente y al médico consultar el historial de citas. | **ADR-08** | Specification (Fowler) |
| **RF-29** | El sistema debe procesar los síntomas registrados por las pacientes en texto libre mediante técnicas de NLP (Procesamiento de Lenguaje Natural). | **ADR-14** | Strategy (GoF) |
| **RF-30** | El sistema debe generar un resumen clínico automatizado del estado reciente de cada paciente utilizando NLP. | **ADR-14** | Strategy (GoF) |
| **RF-31** | El sistema debe identificar síntomas recurrentes y extraer entidades clínicas relevantes del texto libre de la paciente. | **ADR-14** | Strategy (GoF) |
| **RF-32** | El sistema debe clasificar a la paciente en uno de cuatro perfiles de riesgo (Primigestas Sanas, Alto Riesgo Hipertensivo, Multíparas Sanas, Riesgo Metabólico/Obesidad) utilizando un modelo de Machine Learning de clustering (KNN y PCA). | **ADR-06** | Gateway (Fowler) |
| **RF-33** | El sistema debe mostrar al médico la clasificación de riesgo obtenida como apoyo para la toma de decisiones clínicas. | **ADR-06** | Gateway (Fowler) |
| **RF-34** | El sistema debe permitir el envío y recepción de mensajes entre pacientes y recepcionistas. | **ADR-09** | Mediator (GoF) |
| **RF-35** | El sistema debe mostrar el historial completo de conversaciones entre un paciente y el recepcionista. | **ADR-09** | Mediator (GoF) |
| **RF-36** | El sistema debe generar notificaciones para nuevos mensajes no leídos. | **ADR-04** | Observer (GoF) |
| **RF-37** | El sistema debe permitir a las pacientes publicar experiencias e inquietudes en un foro comunitario. | **ADR-13** | Composite (GoF) |
| **RF-38** | El sistema debe permitir la creación y gestión de grupos de apoyo temáticos dentro del foro de la comunidad. | **ADR-13** | Composite (GoF) |
| **RF-39** | El sistema debe permitir a las pacientes comentar e interactuar en las publicaciones de otras usuarias del foro. | **ADR-13** | Composite (GoF) |
| **RF-40** | El sistema debe permitir a los médicos publicar artículos y consejos de salud en la sección de comunidad. | **ADR-13** | Composite (GoF) |
