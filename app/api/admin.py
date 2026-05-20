"""Admin endpoints to fetch all data models."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.customer import Customer
from app.models.driver import Driver
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.ticket import Ticket
from app.schemas.admin import CustomerDetail, DriverDetail, RestaurantDetail
from app.schemas.order import OrderDetail
from app.schemas.ticket import TicketDetail

router = APIRouter(prefix="/admin", tags=["Admin / Debug"])


@router.get("/orders", response_model=list[OrderDetail])
async def list_orders(db: AsyncSession = Depends(get_db)):
    """Fetch all orders in the database."""
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    # Ensure ETA datetime objects are cast to strings or formatted appropriately
    # Pydantic will auto-serialize this if we mapped field type or use from_attributes.
    # Note: ETA timestamp is datetime in model, string in schema, but pydantic handles datetime -> ISO 8601 string conversions out of the box.
    return orders


@router.get("/customers", response_model=list[CustomerDetail])
async def list_customers(db: AsyncSession = Depends(get_db)):
    """Fetch all customers in the database."""
    result = await db.execute(select(Customer))
    return result.scalars().all()


@router.get("/drivers", response_model=list[DriverDetail])
async def list_drivers(db: AsyncSession = Depends(get_db)):
    """Fetch all drivers in the database."""
    result = await db.execute(select(Driver))
    return result.scalars().all()


@router.get("/restaurants", response_model=list[RestaurantDetail])
async def list_restaurants(db: AsyncSession = Depends(get_db)):
    """Fetch all restaurants in the database."""
    result = await db.execute(select(Restaurant))
    return result.scalars().all()


@router.get("/tickets", response_model=list[TicketDetail])
async def list_tickets(db: AsyncSession = Depends(get_db)):
    """Fetch all tickets in the database."""
    result = await db.execute(select(Ticket))
    return result.scalars().all()
