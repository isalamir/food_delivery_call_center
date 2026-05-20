"""Driver intent endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
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
from app.services.driver import (
    get_earnings,
    get_pickup_info,
    report_account_issue,
    report_customer_unreachable,
    report_order_damaged,
)

router = APIRouter(prefix="/driver", tags=["Driver Intents"])


@router.post(
    "/{driver_id}/customer-unreachable",
    response_model=CustomerUnreachableResponse,
    summary="Report customer unreachable",
    description="Initiate customer contact attempt and start no-show timer per policy.",
)
async def customer_unreachable(
    driver_id: str,
    req: CustomerUnreachableRequest,
    db: AsyncSession = Depends(get_db),
) -> CustomerUnreachableResponse:
    return await report_customer_unreachable(db, driver_id, req)


@router.get(
    "/{driver_id}/pickup-info",
    response_model=PickupInfoResponse,
    summary="Get pickup information",
    description="Provide restaurant contact info and pickup instructions.",
)
async def pickup_info(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
) -> PickupInfoResponse:
    return await get_pickup_info(db, driver_id)


@router.post(
    "/{driver_id}/order-damaged",
    response_model=OrderDamagedResponse,
    summary="Report order damaged or spilled",
    description="Log incident, reassign order, adjust driver record accordingly.",
)
async def order_damaged(
    driver_id: str,
    req: OrderDamagedRequest,
    db: AsyncSession = Depends(get_db),
) -> OrderDamagedResponse:
    return await report_order_damaged(db, driver_id, req)


@router.get(
    "/{driver_id}/earnings",
    response_model=EarningsResponse,
    summary="Get earnings breakdown",
    description="Query earnings service and break down trip-level pay.",
)
async def earnings(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
) -> EarningsResponse:
    return await get_earnings(db, driver_id)


@router.post(
    "/{driver_id}/account-issue",
    response_model=AccountIssueResponse,
    summary="Report account or document issue",
    description="Capture request and route to driver operations team.",
)
async def account_issue(
    driver_id: str,
    req: AccountIssueRequest,
    db: AsyncSession = Depends(get_db),
) -> AccountIssueResponse:
    return await report_account_issue(db, driver_id, req)
