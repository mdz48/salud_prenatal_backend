import os

# Sin un .env local con credenciales de base de datos, app.core.database
# revienta al importarse (create_engine(None)). Los tests de este proyecto
# son unitarios (repos mockeados), así que alcanza con una URL válida y
# perezosa: no se ejecuta ninguna query real contra ella.
os.environ.setdefault("LOCAL_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
