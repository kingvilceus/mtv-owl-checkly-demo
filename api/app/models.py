"""ORM model for the funds table.

The raw ``commitment`` column is intentionally **not** mapped: the API must not
select it so a later step can drop it without breaking this code.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import CHAR, BigInteger, Date, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Fund(Base):
    __tablename__ = "funds"

    fund_id: Mapped[str] = mapped_column(Text, primary_key=True)
    fund_name: Mapped[str] = mapped_column(Text)
    manager: Mapped[str] = mapped_column(Text)
    strategy: Mapped[str] = mapped_column(Text)
    vintage_year: Mapped[int] = mapped_column(Integer)
    commitment_cents: Mapped[int | None] = mapped_column(BigInteger)
    currency: Mapped[str | None] = mapped_column(CHAR(3))
    reported_at: Mapped[date] = mapped_column(Date)
