"""Guards the contract migration: the raw commitment column is gone, the parser stays.

Runs against a migrated DB (no seed needed).
"""

from __future__ import annotations

import os

import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://owl:owl@db:5432/owl")


def _funds_columns() -> set[str]:
    with psycopg.connect(DATABASE_URL) as conn:
        return {
            row[0]
            for row in conn.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'funds'"
            ).fetchall()
        }


def test_raw_commitment_column_dropped() -> None:
    columns = _funds_columns()
    assert "commitment" not in columns
    assert {"commitment_cents", "currency"} <= columns


def test_parser_still_available() -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        cents, currency = conn.execute(
            "SELECT commitment_cents, currency FROM parse_commitment(%s)",
            ["$1,000,000 USD"],
        ).fetchone()
    assert cents == 100_000_000
    assert currency.strip() == "USD"
