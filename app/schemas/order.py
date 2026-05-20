from datetime import datetime
from pydantic import BaseModel


class OrderDetail(BaseModel):
    order_id: str
    customer_id: str
    restaurant_id: str
    driver_id: str | None
    status: str
    stage: str
    eta: datetime | None

    total_price: float
    driver_payout: float
    payment_method: str

    class Config:
        from_attributes = True

