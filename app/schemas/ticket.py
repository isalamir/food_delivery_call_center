"""Pydantic schemas for tickets."""

from pydantic import BaseModel


class TicketDetail(BaseModel):
    ticket_id: str
    call_context: dict
    escalation_type: str
    status: str

    class Config:
        from_attributes = True

