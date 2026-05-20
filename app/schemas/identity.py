"""Pydantic schemas for caller identification."""

from pydantic import BaseModel


# ── Request ──────────────────────────────────────────────────────────
class IdentifyRequest(BaseModel):
    """At least one field must be provided. Phone number is tried first,
    then order_id, then partner_id."""

    phone_number: str | None = None
    order_id: str | None = None
    partner_id: str | None = None


# ── Shared context objects ───────────────────────────────────────────
class OrderBrief(BaseModel):
    order_id: str
    status: str
    stage: str
    eta: str | None = None
    total_price: float
    payment_method: str


class CustomerContext(BaseModel):
    customer_id: str
    name: str
    refund_strike_count: int
    active_orders: list[OrderBrief] = []


class RestaurantContext(BaseModel):
    partner_id: str
    name: str
    menu_status: str
    payout_balance: float
    active_incoming_orders: list[OrderBrief] = []


class DriverContext(BaseModel):
    driver_id: str
    name: str
    account_status: str
    pending_earnings: float
    current_assignment: OrderBrief | None = None


# ── Response ─────────────────────────────────────────────────────────
class IdentifyResponse(BaseModel):
    actor_type: str  # 'customer' | 'restaurant' | 'driver'
    context: CustomerContext | RestaurantContext | DriverContext
