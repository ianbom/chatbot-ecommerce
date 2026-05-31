from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.shipping_schema import ShippingRateCheckRequest
from app.service.shipping_service import ShippingRateUnavailable, check_biteship_rates, is_cloudflare_blocked

router = APIRouter(tags=["shipping"])

@router.post("/api/shipping/rates/check", response_model=None)
def check_shipping_rates(payload: ShippingRateCheckRequest) -> dict[str, Any] | JSONResponse:
    try:
        result = check_biteship_rates(payload.model_dump(exclude_none=True))
    except ShippingRateUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    public_result = without_internal_status(result)
    if is_cloudflare_blocked(result):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Biteship request blocked by Cloudflare. Check BITESHIP_USER_AGENT or contact Biteship support.",
                "biteship_error": public_result,
            },
        )
    if result.get("success") is False:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=public_result)
    return public_result

def without_internal_status(payload: dict[str, Any]) -> dict[str, Any]:
    public_payload = dict(payload)
    public_payload.pop("_http_status_code", None)
    return public_payload

