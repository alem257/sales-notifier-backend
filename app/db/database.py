import os
import re
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definida en el entorno")


def ensure_postgres_database(url_string: str) -> None:
    """
    Si la base indicada en DATABASE_URL no existe (p. ej. una BD dedicada tipo `sales`),
    la crea conectando primero a la base de mantenimiento `postgres`.
    Si la URL ya usa la base `postgres`, no hace nada (RDS/local siempre la tienen).
    Solo aplica a URLs postgresql*. Nombres de BD: [a-zA-Z_][a-zA-Z0-9_]*.
    """
    if "postgresql" not in url_string.lower():
        return

    url = make_url(url_string)
    dbname = url.database
    if not dbname or dbname.lower() == "postgres":
        return

    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", dbname):
        raise ValueError(
            f"Nombre de base de datos no permitido para auto-creación: {dbname!r}"
        )

    admin_url = url.set(database="postgres")
    admin_engine = create_engine(
        admin_url,
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": dbname},
        ).first()
        if exists is None:
            # Identificador entre comillas para coincidir con el nombre exacto
            conn.execute(text(f'CREATE DATABASE "{dbname}"'))


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def apply_schema_patches() -> None:
    """Añade columnas nuevas en PostgreSQL (create_all no altera tablas ya existentes)."""
    if not DATABASE_URL or "postgresql" not in DATABASE_URL:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE sales ADD COLUMN IF NOT EXISTS "
                "sync_to_google_sheets BOOLEAN NOT NULL DEFAULT false"
            )
        )
