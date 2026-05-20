"""Driver intent service — business logic for driver calls."""

import random

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.driver import Driver
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.ticket import Ticket
from app.schemas.driver import (
    AccountIssueRequest,
    AccountIssueResponse,
    CustomerUnreachableRequest,
    CustomerUnreachableResponse,
    EarningsResponse,
    OrderDamagedRequest,
    OrderDamagedResponse,
    PickupInfoResponse,
)


async def _get_driver(db: AsyncSession, driver_id: str) -> Driver:
    result = await db.execute(
        select(Driver).where(Driver.driver_id == driver_id)
    )
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    return driver


async def _get_order(db: AsyncSession, order_id: str) -> Order:
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


# ── 1. Customer Unreachable ─────────────────────────────────────────
async def report_customer_unreachable(
    db: AsyncSession, driver_id: str, req: CustomerUnreachableRequest
) -> CustomerUnreachableResponse:
    await _get_driver(db, driver_id)
    await _get_order(db, req.order_id)

    return CustomerUnreachableResponse(
        order_id=req.order_id,
        customer_contact_attempted=True,
        no_show_timer_started=True,
        timeout_seconds=settings.NO_SHOW_TIMEOUT,
        message=f"Customer contact attempted. No-show timer started ({settings.NO_SHOW_TIMEOUT // 60} min). "
        "If the customer does not respond, the order will be marked as undeliverable.",
    )


# ── 2. Navigation / Pickup Issue ────────────────────────────────────
async def get_pickup_info(
    db: AsyncSession, driver_id: str
) -> PickupInfoResponse:
    driver = await _get_driver(db, driver_id)

    if not driver.current_assignment_id:
        raise HTTPException(
            status_code=404, detail="No current delivery assignment."
        )

    order = await _get_order(db, driver.current_assignment_id)

    result = await db.execute(
        select(Restaurant).where(Restaurant.partner_id == order.restaurant_id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found for this order.")

    return PickupInfoResponse(
        order_id=order.order_id,
        restaurant_name=restaurant.name,
        restaurant_phone=restaurant.contact_phone,
        pickup_instructions=restaurant.pickup_instructions or "No special pickup instructions.",
        message=f"Restaurant: {restaurant.name}. Call them at {restaurant.contact_phone} if you need help.",
    )


# ── 3. Order Damaged / Spilled ──────────────────────────────────────
async def report_order_damaged(
    db: AsyncSession, driver_id: str, req: OrderDamagedRequest
) -> OrderDamagedResponse:
    driver = await _get_driver(db, driver_id)
    await _get_order(db, req.order_id)

    # Increment incident count
    driver.incident_count += 1
    await db.commit()

    return OrderDamagedResponse(
        order_id=req.order_id,
        incident_logged=True,
        incident_count=driver.incident_count,
        order_reassigned=True,
        message="Incident logged. A replacement order will be dispatched. "
        f"Your incident count is now {driver.incident_count}.",
    )


# ── 4. Earnings / Tip Question ──────────────────────────────────────
async def get_earnings(
    db: AsyncSession, driver_id: str
) -> EarningsResponse:
    driver = await _get_driver(db, driver_id)

    # Get current trip payout if assigned
    trip_payout = None
    if driver.current_assignment_id:
        order = await _get_order(db, driver.current_assignment_id)
        trip_payout = float(order.driver_payout)

    return EarningsResponse(
        driver_id=driver.driver_id,
        driver_name=driver.name,
        pending_earnings=float(driver.pending_earnings),
        current_trip_payout=trip_payout,
        message=f"Pending earnings: ${float(driver.pending_earnings):.2f}."
        + (f" Current trip payout: ${trip_payout:.2f}." if trip_payout else ""),
    )


# ── 5. Account / Document Issue ─────────────────────────────────────
async def report_account_issue(
    db: AsyncSession, driver_id: str, req: AccountIssueRequest
) -> AccountIssueResponse:
    await _get_driver(db, driver_id)

    ticket = Ticket(
        ticket_id=str(random.randint(1000, 9999)),
        call_context={
            "intent": "account_issue",
            "driver_id": driver_id,
            "description": req.description,
            "issue_type": req.issue_type,
        },
        escalation_type="driver_operations",
        status="pending",
    )
    db.add(ticket)
    await db.commit()

    return AccountIssueResponse(
        ticket_id=ticket.ticket_id,
        routed_to="Driver Operations Team",
        message="Your request has been routed to our Driver Operations team. "
        "You'll receive an update within 24 hours.",
    )
