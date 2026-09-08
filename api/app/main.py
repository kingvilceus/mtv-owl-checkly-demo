"""Minimal read-only API over the funds table (SQLAlchemy).

Serves the parsed money columns (``commitment_cents`` + ``currency``). It never
reads the raw ``commitment`` column, so a later step can drop it safely.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Fund
from app.schemas import FundOut, FundsPage

app = FastAPI(title="OWL Funds API", version="0.2.0")

# Wide-open CORS: this is a local dev tool, not a deployed service.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health(session: Session = Depends(get_session)) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/strategies")
def strategies(session: Session = Depends(get_session)) -> dict[str, list[str]]:
    rows = session.scalars(select(Fund.strategy).distinct().order_by(Fund.strategy)).all()
    return {"strategies": list(rows)}


@app.get("/funds", response_model=FundsPage)
def list_funds(
    session: Session = Depends(get_session),
    strategy: str | None = None,
    limit: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
) -> FundsPage:
    """List funds. Omit ``limit`` to return every matching row."""
    where = (Fund.strategy == strategy,) if strategy else ()

    total = session.scalar(select(func.count()).select_from(Fund).where(*where)) or 0

    stmt = select(Fund).where(*where).order_by(Fund.fund_id).offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    funds = session.scalars(stmt).all()

    return FundsPage(funds=list(funds), total=total, limit=limit, offset=offset)


@app.get("/funds/{fund_id}", response_model=FundOut)
def get_fund(fund_id: str, session: Session = Depends(get_session)) -> Fund:
    fund = session.get(Fund, fund_id)
    if fund is None:
        raise HTTPException(status_code=404, detail="fund not found")
    return fund
