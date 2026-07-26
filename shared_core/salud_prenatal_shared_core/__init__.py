"""Núcleo compartido de los servicios de salud prenatal.

Provee lo común a todos los servicios: base ORM (`Base`, `TimestampMixin`),
conexión a DB, seguridad/JWT, cifrado de campos (`EncryptedString`), enums,
utilidades de tiempo/texto y manejo de errores.

Regla: este paquete NO importa nada de `app.features` ni de ningún `service_*`.
Es hoja del grafo de dependencias.
"""

__version__ = "0.1.0"
