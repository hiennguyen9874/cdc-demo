from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

__all__ = ["Item"]


class Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str | None] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(index=True)
