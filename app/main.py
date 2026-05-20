"""Food Delivery Call Center — FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.customer import router as customer_router
from app.api.driver import router as driver_router
from app.api.identify import router as identify_router
from app.api.restaurant import router as restaurant_router
from app.core.config import settings
from app.db.engine import AsyncSessionLocal, init_db
from app.db.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + seed data. Shutdown: cleanup."""
    await init_db()

    # Seed mock data
    async with AsyncSessionLocal() as session:
        await seed_database(session)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Mock backend for a food delivery call center voice agent. "
        "Identifies callers (customers, restaurants, drivers) and handles "
        "intent-specific actions like refunds, order status, earnings queries, and more."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── Include routers ─────────────────────────────────────────────────
app.include_router(identify_router)
app.include_router(customer_router)
app.include_router(restaurant_router)
app.include_router(driver_router)
app.include_router(admin_router)



@app.get("/", tags=["Health"])
async def root():
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
