"""Pydantic schemas for customer intents."""

from pydantic import BaseModel


# ── Order Status ─────────────────────────────────────────────────────
class OrderStatusResponse(BaseModel):
    order_id: str
    status: str
    stage: str
    eta: str | None
    restaurant_name: str
    driver_name: str | None


# ── Missing / Wrong Items ───────────────────────────────────────────
class MissingItemsRequest(BaseModel):
    order_id: str
    items: list[str]
    description: str = ""


class MissingItemsResponse(BaseModel):
    order_id: str
    logged: bool
    resolution: str  # 'credit_issued' | 'redelivery_triggered' | 'escalated'
    credit_amount: float | None = None
    message: str


# ── Refund Request ───────────────────────────────────────────────────
class RefundRequest(BaseModel):
    order_id: str
    reason: str = ""


class RefundResponse(BaseModel):
    order_id: str
    eligible: bool
    refund_amount: float | None = None
    strikes: int
    message: str


# ── Cancel Active Order ─────────────────────────────────────────────
class CancelOrderRequest(BaseModel):
    order_id: str
    reason: str = ""


class CancelOrderResponse(BaseModel):
    order_id: str
    cancelled: bool
    credit_offered: float | None = None
    message: str


# ── Payment Issue ────────────────────────────────────────────────────
class PaymentIssueResponse(BaseModel):
    order_id: str
    total_price: float
    payment_method: str
    charge_verified: bool
    message: str


# ── Safety / Quality Concern ────────────────────────────────────────
class SafetyConcernRequest(BaseModel):
    order_id: str | None = None
    description: str
    category: str = "general"  # 'food_safety', 'driver_behavior', 'general'


class SafetyConcernResponse(BaseModel):
    ticket_id: str
    escalation_type: str
    follow_up_timeline: str
    message: str
