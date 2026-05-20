"""Order model — the core hub connecting actors."""

import random
from datetime import datetime

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(
        String(10), primary_key=True, default=lambda: str(random.randint(1000, 9999))
    )
    customer_id: Mapped[str] = mapped_column(String(10), nullable=False)
    restaurant_id: Mapped[str] = mapped_column(String(10), nullable=False)
    driver_id: Mapped[str | None] = mapped_column(String(10), nullable=True)

    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="preparing"
    )  # 'preparing', 'picked_up', 'in_transit', 'delivered', 'cancelled'
    stage: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pre-prep"
    )  # 'pre-prep', 'in-prep', 'ready', 'dispatched'
    eta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    driver_payout: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=False, default="cash"
    )  # 'cash', 'visa', 'mastercard', 'apple_pay', 'google_pay'

    def __repr__(self) -> str:
        return f"<Order {self.order_id} status={self.status}>"
