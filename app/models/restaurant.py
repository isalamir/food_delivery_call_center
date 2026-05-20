"""Restaurant model."""

from sqlalchemy import JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    partner_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    menu_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="open"
    )  # 'open' or 'paused'
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    pickup_instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    payout_balance: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    menu_inventory: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<Restaurant {self.name}>"
