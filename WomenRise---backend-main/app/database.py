"""Database engine, session factory, and Base. Provides the get_db dependency."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

# check_same_thread is required for SQLite + FastAPI's threadpool
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
# pool_pre_ping recycles dead connections (e.g. after Neon's compute suspends on idle).
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
