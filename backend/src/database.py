"""Database configuration and session management.

ADR-001: SQLite for all data — single file, WAL mode, zero-config.
"""

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


def get_data_dir() -> Path:
    """Get the data directory for the SQLite database file."""
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_url() -> str:
    """Get the SQLite database URL. Uses WAL mode for concurrent reads during writes."""
    db_path = get_data_dir() / "poker.db"
    return f"sqlite:///{db_path}"


engine = create_engine(
    get_database_url(),
    echo=False,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI async
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode and foreign keys on every connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency: yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
