"""
Database connection setup.

Using SQLite for MVP speed. Schema is written in plain SQLAlchemy
(no SQLite-specific types) so switching to Postgres later is just
changing DATABASE_URL — no model changes needed.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# Override with the DATABASE_URL env var (e.g. a Postgres URL in production,
# or a temp SQLite file in tests). Defaults to a local SQLite file.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./resumefit.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — gives each request its own DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
