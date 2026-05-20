"""Pydantic schemas for restaurant intents."""

from pydantic import BaseModel


# ── Order Clarification ─────────────────────────────────────────────
class OrderClarificationResponse(BaseModel):
    order_id: str
    customer_name: str
    items: list[str]
    special_instructions: str
    payment_method: str
    total_price: float


# ── Item Out of Stock ────────────────────────────────────────────────
class OutOfStockRequest(BaseModel):
    order_id: str
    item_name: str
    substitution_suggestion: str | None = None


class OutOfStockResponse(BaseModel):
    order_id: str
    item_name: str
    customer_notified: bool
    resolution: str  # 'substituted' | 'partial_cancel' | 'pending_customer_response'
    message: str


# ── Tablet / Integration Issue ───────────────────────────────────────
class TabletIssueRequest(BaseModel):
    description: str
    error_code: str | None = None


class TabletIssueResponse(BaseModel):
    ticket_id: str
    diagnostic_steps: list[str]
    message: str


# ── Payout / Billing Question ───────────────────────────────────────
class PayoutResponse(BaseModel):
    partner_id: str
    restaurant_name: str
    payout_balance: float
    recent_orders_count: int
    message: str


# ── Pause / Resume Store ────────────────────────────────────────────
class ToggleStatusRequest(BaseModel):
    action: str  # 'pause' or 'resume'


class ToggleStatusResponse(BaseModel):
    partner_id: str
    previous_status: str
    new_status: str
    message: str
