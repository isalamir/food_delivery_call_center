"""Driver model."""

import random

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Driver(Base):
    __tablename__ = "drivers"

    driver_id: Mapped[str] = mapped_column(
        String(10), primary_key=True, default=lambda: str(random.randint(1000, 9999))
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_assignment_id: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    account_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )  # 'active', 'under_review', "suspended"
    pending_earnings: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    incident_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Driver {self.name}>"
