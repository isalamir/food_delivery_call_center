"""Ticket model for escalation and handover."""

import random

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(
        String(10), primary_key=True, default=lambda: str(random.randint(1000, 9999))
    )
    call_context: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )  # {"transcript": "...", "intent": "...", "actions_taken": "..."}
    escalation_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'safety_concern', 'disputed_liability', 'technical_issue', etc.
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # 'pending', 'resolved', 'escalated_to_supervisor', 'closed'.

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_id} type={self.escalation_type}>"
