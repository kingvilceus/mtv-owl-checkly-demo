"""Minimal read-only API over the funds table.

``commitment`` is returned exactly as it was loaded (raw text); no parsing here.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.db import connect

app = FastAPI(title="OWL Funds API", version="0.1.0")

# Wide-open CORS: this is a local dev tool, not a deployed service.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FUND_COLUMNS = "fund_id, fund_name, manager, strategy, vintage_year, commitment, reported_at"


@app.get("/health")
def health() -> dict[str, str]:
    with connect() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/strategies")
def strategies() -> dict[str, list[str]]:
    with connect() as conn:
        rows = conn.execute("SELECT DISTINCT strategy FROM funds ORDER BY strategy").fetchall()
    return {"strategies": [row["strategy"] for row in rows]}


@app.get("/funds")
def list_funds(
    strategy: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    filters: list[str] = []
    args: list[Any] = []
    if strategy:
        filters.append("strategy = %s")
        args.append(strategy)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    with connect() as conn:
        total = conn.execute(f"SELECT count(*) AS n FROM funds {where}", args).fetchone()["n"]
        rows = conn.execute(
            f"SELECT {FUND_COLUMNS} FROM funds {where} ORDER BY fund_id LIMIT %s OFFSET %s",
            [*args, limit, offset],
        ).fetchall()

    return {"funds": rows, "total": total, "limit": limit, "offset": offset}


@app.get("/funds/{fund_id}")
def get_fund(fund_id: str) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute(
            f"SELECT {FUND_COLUMNS} FROM funds WHERE fund_id = %s", [fund_id]
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="fund not found")
    return row
