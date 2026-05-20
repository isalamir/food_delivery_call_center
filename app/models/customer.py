"""Customer model."""

import random

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(
        String(10), primary_key=True, default=lambda: str(random.randint(1000, 9999))
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    active_order_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    refund_strike_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Customer {self.name}>"
