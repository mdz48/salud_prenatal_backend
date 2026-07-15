from functools import lru_cache
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from salud_prenatal_shared_core.time import now_cdmx

load_dotenv()

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=now_cdmx, nullable=False)
    updated_at = Column(DateTime, default=now_cdmx, onupdate=now_cdmx, nullable=False)


def _resolve_database_url() -> str:
    # DATABASE_URL overrides everything (used by tests); otherwise RDS with LOCAL_URL fallback
    override = os.getenv("DATABASE_URL")
    if override:
        return override

    rds_url = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    try:
        probe = create_engine(rds_url, pool_pre_ping=True)
        with probe.connect():
            pass
        probe.dispose()
        return rds_url
    except Exception as e:
        print(f"Error al conectar a la base de datos RDS, conectando a localhost para desarrollo: {e}")
        return os.getenv("LOCAL_URL")


@lru_cache
def get_engine():
    url = _resolve_database_url()
    engine_kwargs = {"pool_pre_ping": True, "pool_recycle": 1800}
    # keepalives TCP: evita que RDS/firewall corte conexiones idle sin avisar
    # (la caida "server closed the connection unexpectedly" a mitad de query).
    # Solo aplica a postgres; con SQLite (tests) estos connect_args no son validos.
    if url and url.startswith(("postgresql", "postgres")):
        engine_kwargs["connect_args"] = {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
    return create_engine(url, **engine_kwargs)


@lru_cache
def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
