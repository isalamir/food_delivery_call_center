"""Identity service — caller identification logic."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.driver import Driver
from app.models.identity import IdentityLookup
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.schemas.identity import (
    CustomerContext,
    DriverContext,
    IdentifyResponse,
    OrderBrief,
    RestaurantContext,
)


def _order_to_brief(order: Order) -> OrderBrief:
    return OrderBrief(
        order_id=order.order_id,
        status=order.status,
        stage=order.stage,
        eta=str(order.eta) if order.eta else None,
        total_price=float(order.total_price),
        payment_method=order.payment_method,
    )


async def _build_customer_context(
    db: AsyncSession, customer: Customer
) -> IdentifyResponse:
    """Build full customer context with active orders."""
    orders = []
    if customer.active_order_id:
        result = await db.execute(
            select(Order).where(Order.order_id == customer.active_order_id)
        )
        order = result.scalar_one_or_none()
        if order:
            orders.append(_order_to_brief(order))

    return IdentifyResponse(
        actor_type="customer",
        context=CustomerContext(
            customer_id=customer.customer_id,
            name=customer.name,
            refund_strike_count=customer.refund_strike_count,
            active_orders=orders,
        ),
    )


async def _build_restaurant_context(
    db: AsyncSession, restaurant: Restaurant
) -> IdentifyResponse:
    """Build restaurant context with active incoming orders."""
    result = await db.execute(
        select(Order).where(
            Order.restaurant_id == restaurant.partner_id,
            Order.status.in_(["preparing", "picked_up"]),
        )
    )
    orders = [_order_to_brief(o) for o in result.scalars().all()]

    return IdentifyResponse(
        actor_type="restaurant",
        context=RestaurantContext(
            partner_id=restaurant.partner_id,
            name=restaurant.name,
            menu_status=restaurant.menu_status,
            payout_balance=float(restaurant.payout_balance),
            active_incoming_orders=orders,
        ),
    )


async def _build_driver_context(
    db: AsyncSession, driver: Driver
) -> IdentifyResponse:
    """Build driver context with current assignment."""
    assignment = None
    if driver.current_assignment_id:
        result = await db.execute(
            select(Order).where(Order.order_id == driver.current_assignment_id)
        )
        order = result.scalar_one_or_none()
        if order:
            assignment = _order_to_brief(order)

    return IdentifyResponse(
        actor_type="driver",
        context=DriverContext(
            driver_id=driver.driver_id,
            name=driver.name,
            account_status=driver.account_status,
            pending_earnings=float(driver.pending_earnings),
            current_assignment=assignment,
        ),
    )


# ── Context builder dispatch ────────────────────────────────────────
_CONTEXT_BUILDERS = {
    "customer": (Customer, "customer_id", _build_customer_context),
    "restaurant": (Restaurant, "partner_id", _build_restaurant_context),
    "driver": (Driver, "driver_id", _build_driver_context),
}


async def identify_by_phone(
    db: AsyncSession, phone_number: str
) -> IdentifyResponse:
    """Primary path: look up phone number in identity_lookup."""
    result = await db.execute(
        select(IdentityLookup).where(IdentityLookup.phone_number == phone_number)
    )
    identity = result.scalar_one_or_none()
    if not identity:
        raise HTTPException(status_code=404, detail="Phone number not recognized.")

    model_cls, pk_field, builder = _CONTEXT_BUILDERS[identity.actor_type]
    result = await db.execute(
        select(model_cls).where(getattr(model_cls, pk_field) == identity.linked_id)
    )
    actor = result.scalar_one_or_none()
    if not actor:
        raise HTTPException(status_code=404, detail="Linked actor record not found.")

    return await builder(db, actor)


async def identify_by_order_id(
    db: AsyncSession, order_id: str
) -> IdentifyResponse:
    """Fallback: resolve an order ID to the customer who placed it."""
    result = await db.execute(
        select(Order).where(Order.order_id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order ID not found.")

    result = await db.execute(
        select(Customer).where(Customer.customer_id == order.customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer for this order not found.")

    return await _build_customer_context(db, customer)


async def identify_by_partner_id(
    db: AsyncSession, partner_id: str
) -> IdentifyResponse:
    """Fallback: resolve a partner ID directly to a restaurant."""
    result = await db.execute(
        select(Restaurant).where(Restaurant.partner_id == partner_id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Partner ID not found.")

    return await _build_restaurant_context(db, restaurant)
