"""Database connection helper.

The API only ever reads ``DATABASE_URL`` from the environment, so the same code
can be pointed at any Postgres instance (local compose DB, or a shared one when
replaying two checkouts side by side).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://owl:owl@db:5432/owl")


@contextmanager
def connect() -> Iterator[psycopg.Connection]:
    """Yield a short-lived connection with dict rows, committing on clean exit."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn
