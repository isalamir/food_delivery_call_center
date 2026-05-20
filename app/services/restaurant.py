"""Restaurant intent service — business logic for restaurant calls."""

import random

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.ticket import Ticket
from app.schemas.restaurant import (
    OrderClarificationResponse,
    OutOfStockRequest,
    OutOfStockResponse,
    PayoutResponse,
    TabletIssueRequest,
    TabletIssueResponse,
    ToggleStatusRequest,
    ToggleStatusResponse,
)


async def _get_restaurant(db: AsyncSession, partner_id: str) -> Restaurant:
    result = await db.execute(
        select(Restaurant).where(Restaurant.partner_id == partner_id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    return restaurant


async def _get_order(db: AsyncSession, order_id: str) -> Order:
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


# ── 1. Order Clarification ──────────────────────────────────────────
async def get_order_clarification(
    db: AsyncSession, partner_id: str, order_id: str
) -> OrderClarificationResponse:
    await _get_restaurant(db, partner_id)
    order = await _get_order(db, order_id)

    # Verify the order belongs to this restaurant
    if order.restaurant_id != partner_id:
        raise HTTPException(
            status_code=403, detail="This order does not belong to your restaurant."
        )

    # Mock order items (in a real system these come from an order_items table)
    return OrderClarificationResponse(
        order_id=order.order_id,
        customer_name="Customer",  # Simplified — would join to customer table
        items=["Item details available in full order system"],
        special_instructions="No special instructions on file.",
        payment_method=order.payment_method,
        total_price=float(order.total_price),
    )


# ── 2. Item Out of Stock ────────────────────────────────────────────
async def report_out_of_stock(
    db: AsyncSession, partner_id: str, req: OutOfStockRequest
) -> OutOfStockResponse:
    restaurant = await _get_restaurant(db, partner_id)
    await _get_order(db, req.order_id)

    # Update menu inventory
    inventory = dict(restaurant.menu_inventory) if restaurant.menu_inventory else {}
    inventory[req.item_name] = False
    restaurant.menu_inventory = inventory
    await db.commit()

    resolution = "substituted" if req.substitution_suggestion else "partial_cancel"
    message = (
        f"Customer will be notified about '{req.item_name}'. "
        f"Suggested substitution: {req.substitution_suggestion}."
        if req.substitution_suggestion
        else f"Customer will be notified. '{req.item_name}' marked as unavailable."
    )

    return OutOfStockResponse(
        order_id=req.order_id,
        item_name=req.item_name,
        customer_notified=True,
        resolution=resolution,
        message=message,
    )


# ── 3. Tablet / Integration Issue ───────────────────────────────────
async def report_tablet_issue(
    db: AsyncSession, partner_id: str, req: TabletIssueRequest
) -> TabletIssueResponse:
    await _get_restaurant(db, partner_id)

    ticket = Ticket(
        ticket_id=str(random.randint(1000, 9999)),
        call_context={
            "intent": "tablet_issue",
            "partner_id": partner_id,
            "description": req.description,
            "error_code": req.error_code,
        },
        escalation_type="technical_issue",
        status="pending",
    )
    db.add(ticket)
    await db.commit()

    return TabletIssueResponse(
        ticket_id=ticket.ticket_id,
        diagnostic_steps=[
            "1. Force-close the app and reopen it.",
            "2. Check your Wi-Fi connection and restart the router if needed.",
            "3. Restart the tablet completely.",
            "4. If the issue persists, our tech team will follow up within 30 minutes.",
        ],
        message="A technical support ticket has been created. Please try the diagnostic steps.",
    )


# ── 4. Payout / Billing Question ────────────────────────────────────
async def get_payout_info(
    db: AsyncSession, partner_id: str
) -> PayoutResponse:
    restaurant = await _get_restaurant(db, partner_id)

    # Count recent orders
    result = await db.execute(
        select(func.count()).where(Order.restaurant_id == partner_id)
    )
    order_count = result.scalar() or 0

    return PayoutResponse(
        partner_id=restaurant.partner_id,
        restaurant_name=restaurant.name,
        payout_balance=float(restaurant.payout_balance),
        recent_orders_count=order_count,
        message=f"Current payout balance: ${float(restaurant.payout_balance):.2f} across {order_count} orders.",
    )


# ── 5. Pause / Resume Store ─────────────────────────────────────────
async def toggle_store_status(
    db: AsyncSession, partner_id: str, req: ToggleStatusRequest
) -> ToggleStatusResponse:
    restaurant = await _get_restaurant(db, partner_id)

    previous = restaurant.menu_status
    new_status = "paused" if req.action == "pause" else "open"

    if previous == new_status:
        return ToggleStatusResponse(
            partner_id=restaurant.partner_id,
            previous_status=previous,
            new_status=new_status,
            message=f"Store is already {new_status}. No change needed.",
        )

    restaurant.menu_status = new_status
    await db.commit()

    return ToggleStatusResponse(
        partner_id=restaurant.partner_id,
        previous_status=previous,
        new_status=new_status,
        message=f"Store status changed from '{previous}' to '{new_status}'.",
    )
