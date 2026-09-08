"""Exercises the parse_commitment() SQL function against representative inputs.

Needs the DB migrated (the function exists after migration 0002); it does not need
seeded data. Run with `make test`.
"""

from __future__ import annotations

import os

import psycopg
import pytest

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://owl:owl@db:5432/owl")

# (raw commitment, expected cents, expected currency)
CASES = [
    ("$15,000,000 USD", 1_500_000_000, "USD"),
    ("USD 10,000,000", 1_000_000_000, "USD"),
    ("£12,500,000 GBP", 1_250_000_000, "GBP"),
    ("€40,000,000 EUR", 4_000_000_000, "EUR"),
    ("¥1,125,000,000 JPY", 112_500_000_000, "JPY"),
    ("$500,000", 50_000_000, "USD"),
    ("1250000 USD", 125_000_000, "USD"),
    ("~$1,000,000 USD", 100_000_000, "USD"),
    ("$3,000,000 usd", 300_000_000, "USD"),
    ("$10,000,000.25 USD", 1_000_000_025, "USD"),
    ("$5,000,000.75 USD", 500_000_075, "USD"),
    ("Not reported", None, None),
    ("Undisclosed", None, None),
    ("TBD", None, None),
    ("", None, None),
    (None, None, None),
]


@pytest.fixture(scope="module")
def conn() -> psycopg.Connection:
    with psycopg.connect(DATABASE_URL) as connection:
        yield connection


@pytest.mark.parametrize(("raw", "cents", "currency"), CASES)
def test_parse_commitment(
    conn: psycopg.Connection, raw: str | None, cents: int | None, currency: str | None
) -> None:
    got_cents, got_currency = conn.execute(
        "SELECT commitment_cents, currency FROM parse_commitment(%s)", [raw]
    ).fetchone()
    assert got_cents == cents
    assert (got_currency.strip() if got_currency else got_currency) == currency
