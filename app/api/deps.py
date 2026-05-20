"""FastAPI dependencies — database session injection."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a DB session that auto-closes after the request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
