"""Caller identification endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.identity import IdentifyRequest, IdentifyResponse
from app.services.identity import (
    identify_by_order_id,
    identify_by_partner_id,
    identify_by_phone,
)

router = APIRouter(tags=["Identification"])


@router.post(
    "/identify",
    response_model=IdentifyResponse,
    summary="Identify a caller",
    description=(
        "Identifies the caller by phone number, order ID, or partner ID. "
        "Phone number is tried first, then order_id (resolves to customer), "
        "then partner_id (resolves to restaurant). "
        "At least one identifier must be provided."
    ),
)
async def identify_caller(
    req: IdentifyRequest,
    db: AsyncSession = Depends(get_db),
) -> IdentifyResponse:
    # Validate that at least one identifier is provided
    if not any([req.phone_number, req.order_id, req.partner_id]):
        raise HTTPException(
            status_code=400,
            detail="At least one identifier must be provided: phone_number, order_id, or partner_id.",
        )

    # 1. Try phone number first (primary path)
    if req.phone_number:
        try:
            return await identify_by_phone(db, req.phone_number)
        except HTTPException:
            # Phone not found, fall through to next method
            if not req.order_id and not req.partner_id:
                raise

    # 2. Try order ID (resolves to customer)
    if req.order_id:
        try:
            return await identify_by_order_id(db, req.order_id)
        except HTTPException:
            if not req.partner_id:
                raise

    # 3. Try partner ID (resolves to restaurant)
    if req.partner_id:
        return await identify_by_partner_id(db, req.partner_id)

    raise HTTPException(status_code=404, detail="Could not identify caller with the provided information.")
