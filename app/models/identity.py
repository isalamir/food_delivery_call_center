"""Identity lookup model — routes callers to the correct actor."""

import random

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IdentityLookup(Base):
    __tablename__ = "identity_lookup"

    identity_id: Mapped[str] = mapped_column(
        String(10), primary_key=True, default=lambda: str(random.randint(1000, 9999))
    )
    phone_number: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, unique=True
    )
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'customer', 'restaurant', 'driver'
    linked_id: Mapped[str] = mapped_column(String(10), nullable=False)

    def __repr__(self) -> str:
        return f"<Identity {self.phone_number} -> {self.actor_type}>"
