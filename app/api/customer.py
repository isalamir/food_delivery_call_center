"""Customer intent endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
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
from app.services.customer import (
    cancel_order,
    check_payment_issue,
    get_order_status,
    report_missing_items,
    report_safety_concern,
    request_refund,
)

router = APIRouter(prefix="/customer", tags=["Customer Intents"])


@router.get(
    "/{customer_id}/order-status",
    response_model=OrderStatusResponse,
    summary="Get order status",
    description="Query real-time status and ETA for the customer's active order.",
)
async def order_status(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
) -> OrderStatusResponse:
    return await get_order_status(db, customer_id)


@router.post(
    "/{customer_id}/missing-items",
    response_model=MissingItemsResponse,
    summary="Report missing or wrong items",
    description="Log an item-level complaint. Issues credit or triggers redelivery per policy.",
)
async def missing_items(
    customer_id: str,
    req: MissingItemsRequest,
    db: AsyncSession = Depends(get_db),
) -> MissingItemsResponse:
    return await report_missing_items(db, customer_id, req)


@router.post(
    "/{customer_id}/refund",
    response_model=RefundResponse,
    summary="Request a refund",
    description="Check refund eligibility against policy, process or explain denial.",
)
async def refund(
    customer_id: str,
    req: RefundRequest,
    db: AsyncSession = Depends(get_db),
) -> RefundResponse:
    return await request_refund(db, customer_id, req)


@router.post(
    "/{customer_id}/cancel",
    response_model=CancelOrderResponse,
    summary="Cancel active order",
    description="Cancel if pre-preparation stage; otherwise offer credit.",
)
async def cancel(
    customer_id: str,
    req: CancelOrderRequest,
    db: AsyncSession = Depends(get_db),
) -> CancelOrderResponse:
    return await cancel_order(db, customer_id, req)


@router.get(
    "/{customer_id}/payment-issue",
    response_model=PaymentIssueResponse,
    summary="Check payment issue",
    description="Verify charge against payment service and explain.",
)
async def payment_issue(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
) -> PaymentIssueResponse:
    return await check_payment_issue(db, customer_id)


@router.post(
    "/{customer_id}/safety-concern",
    response_model=SafetyConcernResponse,
    summary="Report safety or quality concern",
    description="Capture details, create priority ticket, confirm follow-up timeline.",
)
async def safety_concern(
    customer_id: str,
    req: SafetyConcernRequest,
    db: AsyncSession = Depends(get_db),
) -> SafetyConcernResponse:
    return await report_safety_concern(db, customer_id, req)
