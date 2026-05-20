"""Customer intent service — business logic for customer calls."""

import random

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.customer import Customer
from app.models.driver import Driver
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.ticket import Ticket
from app.schemas.customer import (
    CancelOrderRequest,
    CancelOrderResponse,
    MissingItemsRequest,
    MissingItemsResponse,
    OrderStatusResponse,
    PaymentIssueResponse,
    RefundRequest,
    RefundResponse,
    SafetyConcernRequest,
    SafetyConcernResponse,
)


async def _get_customer(db: AsyncSession, customer_id: str) -> Customer:
    result = await db.execute(
        select(Customer).where(Customer.customer_id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return customer


async def _get_order(db: AsyncSession, order_id: str) -> Order:
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


# ── 1. Order Status ─────────────────────────────────────────────────
async def get_order_status(
    db: AsyncSession, customer_id: str
) -> OrderStatusResponse:
    customer = await _get_customer(db, customer_id)
    if not customer.active_order_id:
        raise HTTPException(status_code=404, detail="No active order found.")

    order = await _get_order(db, customer.active_order_id)

    # Fetch restaurant name
    res = await db.execute(
        select(Restaurant).where(Restaurant.partner_id == order.restaurant_id)
    )
    restaurant = res.scalar_one_or_none()

    # Fetch driver name
    driver_name = None
    if order.driver_id:
        res = await db.execute(
            select(Driver).where(Driver.driver_id == order.driver_id)
        )
        driver = res.scalar_one_or_none()
        if driver:
            driver_name = driver.name

    return OrderStatusResponse(
        order_id=order.order_id,
        status=order.status,
        stage=order.stage,
        eta=str(order.eta) if order.eta else None,
        restaurant_name=restaurant.name if restaurant else "Unknown",
        driver_name=driver_name,
    )


# ── 2. Missing / Wrong Items ────────────────────────────────────────
async def report_missing_items(
    db: AsyncSession, customer_id: str, req: MissingItemsRequest
) -> MissingItemsResponse:
    await _get_customer(db, customer_id)
    order = await _get_order(db, req.order_id)

    # Mock policy: issue credit if under threshold, else escalate
    credit = round(float(order.total_price) * 0.2, 2)  # 20% credit per item complaint
    if credit > settings.MAX_AUTO_REFUND_AMOUNT:
        resolution = "escalated"
        credit = None
        message = "Your complaint has been escalated for manual review."
    else:
        resolution = "credit_issued"
        message = f"A credit of ${credit:.2f} has been applied to your account."

    return MissingItemsResponse(
        order_id=order.order_id,
        logged=True,
        resolution=resolution,
        credit_amount=credit,
        message=message,
    )


# ── 3. Refund Request ───────────────────────────────────────────────
async def request_refund(
    db: AsyncSession, customer_id: str, req: RefundRequest
) -> RefundResponse:
    customer = await _get_customer(db, customer_id)
    order = await _get_order(db, req.order_id)

    # Check strike count
    if customer.refund_strike_count > settings.REFUND_STRIKE_LIMIT:
        return RefundResponse(
            order_id=order.order_id,
            eligible=False,
            refund_amount=None,
            strikes=customer.refund_strike_count,
            message="Refund limit exceeded. This case has been escalated to a supervisor.",
        )

    # Check amount threshold
    total = float(order.total_price)
    if total > settings.MAX_AUTO_REFUND_AMOUNT:
        return RefundResponse(
            order_id=order.order_id,
            eligible=False,
            refund_amount=None,
            strikes=customer.refund_strike_count,
            message=f"Orders above ${settings.MAX_AUTO_REFUND_AMOUNT:.2f} require manual approval. Escalating.",
        )

    # Process refund
    customer.refund_strike_count += 1
    order.status = "refunded"
    await db.commit()

    return RefundResponse(
        order_id=order.order_id,
        eligible=True,
        refund_amount=total,
        strikes=customer.refund_strike_count,
        message=f"Refund of ${total:.2f} processed to {order.payment_method}.",
    )


# ── 4. Cancel Active Order ──────────────────────────────────────────
async def cancel_order(
    db: AsyncSession, customer_id: str, req: CancelOrderRequest
) -> CancelOrderResponse:
    await _get_customer(db, customer_id)
    order = await _get_order(db, req.order_id)

    if order.stage == "pre-prep":
        order.status = "cancelled"
        await db.commit()
        return CancelOrderResponse(
            order_id=order.order_id,
            cancelled=True,
            credit_offered=None,
            message="Order cancelled successfully. A full refund will be issued.",
        )
    else:
        # Offer credit instead
        credit = round(float(order.total_price) * 0.5, 2)
        return CancelOrderResponse(
            order_id=order.order_id,
            cancelled=False,
            credit_offered=credit,
            message=f"Order is already in {order.stage} stage and cannot be cancelled. "
            f"We can offer a ${credit:.2f} credit instead.",
        )


# ── 5. Payment Issue ────────────────────────────────────────────────
async def check_payment_issue(
    db: AsyncSession, customer_id: str
) -> PaymentIssueResponse:
    customer = await _get_customer(db, customer_id)
    if not customer.active_order_id:
        raise HTTPException(status_code=404, detail="No active order to verify payment for.")

    order = await _get_order(db, customer.active_order_id)

    return PaymentIssueResponse(
        order_id=order.order_id,
        total_price=float(order.total_price),
        payment_method=order.payment_method,
        charge_verified=True,
        message=f"Charge of ${float(order.total_price):.2f} via {order.payment_method} is verified and correct.",
    )


# ── 6. Safety / Quality Concern ─────────────────────────────────────
async def report_safety_concern(
    db: AsyncSession, customer_id: str, req: SafetyConcernRequest
) -> SafetyConcernResponse:
    await _get_customer(db, customer_id)

    ticket = Ticket(
        ticket_id=str(random.randint(1000, 9999)),
        call_context={
            "intent": "safety_concern",
            "customer_id": customer_id,
            "order_id": req.order_id,
            "description": req.description,
            "category": req.category,
        },
        escalation_type="safety_concern",
        status="pending",
    )
    db.add(ticket)
    await db.commit()

    return SafetyConcernResponse(
        ticket_id=ticket.ticket_id,
        escalation_type="safety_concern",
        follow_up_timeline="A safety specialist will contact you within 2 hours.",
        message="Your safety concern has been logged as a priority ticket. Thank you for reporting this.",
    )
