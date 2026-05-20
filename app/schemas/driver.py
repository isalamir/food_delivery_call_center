"""Pydantic schemas for driver intents."""

from pydantic import BaseModel


# ── Customer Unreachable ─────────────────────────────────────────────
class CustomerUnreachableRequest(BaseModel):
    order_id: str
    attempts_made: int = 1


class CustomerUnreachableResponse(BaseModel):
    order_id: str
    customer_contact_attempted: bool
    no_show_timer_started: bool
    timeout_seconds: int
    message: str


# ── Navigation / Pickup Issue ───────────────────────────────────────
class PickupInfoResponse(BaseModel):
    order_id: str
    restaurant_name: str
    restaurant_phone: str
    pickup_instructions: str
    message: str


# ── Order Damaged / Spilled ─────────────────────────────────────────
class OrderDamagedRequest(BaseModel):
    order_id: str
    description: str


class OrderDamagedResponse(BaseModel):
    order_id: str
    incident_logged: bool
    incident_count: int
    order_reassigned: bool
    message: str


# ── Earnings / Tip Question ─────────────────────────────────────────
class EarningsResponse(BaseModel):
    driver_id: str
    driver_name: str
    pending_earnings: float
    current_trip_payout: float | None = None
    message: str


# ── Account / Document Issue ────────────────────────────────────────
class AccountIssueRequest(BaseModel):
    description: str
    issue_type: str = "general"  # 'document_upload', 'account_locked', 'general'


class AccountIssueResponse(BaseModel):
    ticket_id: str
    routed_to: str
    message: str
