"""Restaurant intent endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
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
from app.services.restaurant import (
    get_order_clarification,
    get_payout_info,
    report_out_of_stock,
    report_tablet_issue,
    toggle_store_status,
)

router = APIRouter(prefix="/restaurant", tags=["Restaurant Intents"])


@router.get(
    "/{partner_id}/order/{order_id}",
    response_model=OrderClarificationResponse,
    summary="Get order details",
    description="Pull order details including special instructions and read back to restaurant.",
)
async def order_clarification(
    partner_id: str,
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> OrderClarificationResponse:
    return await get_order_clarification(db, partner_id, order_id)


@router.post(
    "/{partner_id}/out-of-stock",
    response_model=OutOfStockResponse,
    summary="Report item out of stock",
    description="Notify customer, offer substitution or partial cancellation.",
)
async def out_of_stock(
    partner_id: str,
    req: OutOfStockRequest,
    db: AsyncSession = Depends(get_db),
) -> OutOfStockResponse:
    return await report_out_of_stock(db, partner_id, req)


@router.post(
    "/{partner_id}/tablet-issue",
    response_model=TabletIssueResponse,
    summary="Report tablet or integration issue",
    description="Run diagnostic prompts, guide restart, or log technical ticket.",
)
async def tablet_issue(
    partner_id: str,
    req: TabletIssueRequest,
    db: AsyncSession = Depends(get_db),
) -> TabletIssueResponse:
    return await report_tablet_issue(db, partner_id, req)


@router.get(
    "/{partner_id}/payout",
    response_model=PayoutResponse,
    summary="Get payout information",
    description="Query payout service and summarize recent transactions.",
)
async def payout(
    partner_id: str,
    db: AsyncSession = Depends(get_db),
) -> PayoutResponse:
    return await get_payout_info(db, partner_id)


@router.post(
    "/{partner_id}/toggle-status",
    response_model=ToggleStatusResponse,
    summary="Pause or resume store",
    description="Toggle store availability status.",
)
async def toggle_status(
    partner_id: str,
    req: ToggleStatusRequest,
    db: AsyncSession = Depends(get_db),
) -> ToggleStatusResponse:
    return await toggle_store_status(db, partner_id, req)
