"""Pydantic response models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class FundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fund_id: str
    fund_name: str
    manager: str
    strategy: str
    vintage_year: int
    commitment_cents: int | None
    currency: str | None
    reported_at: date

    @field_validator("currency")
    @classmethod
    def _trim_currency(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class FundsPage(BaseModel):
    funds: list[FundOut]
    total: int
    limit: int | None
    offset: int
