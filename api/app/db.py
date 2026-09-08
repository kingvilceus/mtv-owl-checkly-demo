"""SQLAlchemy engine + session wiring.

The API only reads ``DATABASE_URL`` from the environment, so it can point at any
Postgres instance (the compose DB, or a shared one for a side-by-side replay).
The URL is normalised to the psycopg (v3) driver.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

RAW_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://owl:owl@db:5432/owl")


def _sqlalchemy_url(raw: str) -> str:
    for prefix in ("postgresql://", "postgres://"):
        if raw.startswith(prefix):
            return "postgresql+psycopg://" + raw[len(prefix) :]
    return raw  # already has an explicit driver, e.g. postgresql+psycopg://


engine = create_engine(_sqlalchemy_url(RAW_DATABASE_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: a session scoped to one request."""
    with SessionLocal() as session:
        yield session
