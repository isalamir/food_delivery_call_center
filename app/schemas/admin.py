"""Pydantic schemas for administrative list views."""

from pydantic import BaseModel


class CustomerDetail(BaseModel):
    customer_id: str
    name: str
    active_order_id: str | None
    refund_strike_count: int

    class Config:
        from_attributes = True


class DriverDetail(BaseModel):
    driver_id: str
    name: str
    current_assignment_id: str | None
    account_status: str
    pending_earnings: float
    incident_count: int

    class Config:
        from_attributes = True


class RestaurantDetail(BaseModel):
    partner_id: str
    name: str
    menu_status: str
    contact_phone: str
    pickup_instructions: str
    payout_balance: float
    menu_inventory: dict

    class Config:
        from_attributes = True
