"""Drop and recreate the database, apply every migration, load ``funds.csv``.

Invoked by ``make seed`` inside the api container. Honors ``DATABASE_URL`` so it
can target any Postgres instance. The CSV's raw ``commitment`` text is loaded into
a temp table and turned into ``commitment_cents`` + ``currency`` by the same
``parse_commitment()`` SQL function the migrations use.
"""

from __future__ import annotations

import csv
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import psycopg
from psycopg import sql

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "funds.csv"

# Columns as they appear in funds.csv (still includes the raw `commitment`).
CSV_COLUMNS = (
    "fund_id",
    "fund_name",
    "manager",
    "strategy",
    "vintage_year",
    "commitment",
    "reported_at",
)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://owl:owl@db:5432/owl")


def _maintenance_url(database_url: str) -> tuple[str, str]:
    """Return (url pointing at the `postgres` db, target database name)."""
    parsed = urlparse(database_url)
    target_db = parsed.path.lstrip("/")
    if not target_db:
        raise SystemExit("DATABASE_URL must include a database name")
    return urlunparse(parsed._replace(path="/postgres")), target_db


def recreate_database() -> None:
    maint_url, target_db = _maintenance_url(DATABASE_URL)
    with psycopg.connect(maint_url, autocommit=True) as conn:
        conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = %s AND pid <> pg_backend_pid()",
            [target_db],
        )
        conn.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target_db)))
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
    print(f"recreated database {target_db!r}")


def apply_migrations() -> None:
    subprocess.run(
        ["yoyo", "apply", "--batch", "--database", DATABASE_URL],
        cwd=REPO_ROOT,
        check=True,
    )


STAGING_DDL = """
CREATE TEMP TABLE funds_import (
    fund_id text,
    fund_name text,
    manager text,
    strategy text,
    vintage_year integer,
    commitment text,
    reported_at date
)
"""

INSERT_FROM_STAGING = """
INSERT INTO funds (
    fund_id, fund_name, manager, strategy, vintage_year,
    commitment_cents, currency, reported_at
)
SELECT
    i.fund_id, i.fund_name, i.manager, i.strategy, i.vintage_year,
    p.commitment_cents, p.currency, i.reported_at
FROM funds_import AS i, LATERAL parse_commitment(i.commitment) AS p
"""


def load_csv() -> int:
    copy_sql = f"COPY funds_import ({', '.join(CSV_COLUMNS)}) FROM STDIN"
    count = 0
    with (
        CSV_PATH.open(newline="", encoding="utf-8") as fh,
        psycopg.connect(DATABASE_URL) as conn,
    ):
        reader = csv.DictReader(fh)
        with conn.cursor() as cur:
            cur.execute(STAGING_DDL)
            with cur.copy(copy_sql) as copy:
                for row in reader:
                    copy.write_row(
                        (
                            row["fund_id"],
                            row["fund_name"],
                            row["manager"],
                            row["strategy"],
                            int(row["vintage_year"]),
                            row["commitment"] or None,
                            row["reported_at"],
                        )
                    )
                    count += 1
            cur.execute(INSERT_FROM_STAGING)
        conn.commit()
    return count


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"missing data file: {CSV_PATH}")
    recreate_database()
    apply_migrations()
    loaded = load_csv()
    with psycopg.connect(DATABASE_URL) as conn:
        total = conn.execute("SELECT count(*) FROM funds").fetchone()[0]
    print(f"loaded {loaded} rows; funds table now has {total}")


if __name__ == "__main__":
    main()
