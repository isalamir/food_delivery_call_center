"""Async database engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # SQLite needs this for async
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables. Called once on app startup."""
    from app.db.base import Base
    # Import all models so they register with Base.metadata
    import app.models.identity  # noqa: F401
    import app.models.customer  # noqa: F401
    import app.models.restaurant  # noqa: F401
    import app.models.driver  # noqa: F401
    import app.models.order  # noqa: F401
    import app.models.ticket  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
