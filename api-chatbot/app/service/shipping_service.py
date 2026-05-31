from decimal import Decimal
from typing import Protocol

import httpx

from app.core.config import get_settings

BITESHIP_RATES_PATH = "/v1/rates/couriers"
BITESHIP_AREAS_PATH = "/v1/maps/areas"

class ShippingRateUnavailable(RuntimeError):
    def __init__(self, message: str, attempts: list[str] | None = None) -> None:
        super().__init__(message)
        self.attempts = attempts or []

class BiteshipCloudflareBlocked(ShippingRateUnavailable):
    def __init__(self, payload: dict) -> None:
        super().__init__("Biteship request blocked by Cloudflare")
        self.payload = payload

class ShippingClient(Protocol):
    def get_shipping_quotes(self, destination: dict[str, str], items: list[dict[str, object]]) -> list[dict[str, object]]: ...

class BiteshipShippingClient:
    def get_shipping_quotes(self, destination: dict[str, str], items: list[dict[str, object]]) -> list[dict[str, object]]:
        settings = get_settings()
        api_key = get_biteship_api_key(settings)
        if not api_key or api_key.startswith("change-me"):
            raise ShippingRateUnavailable("BITESHIP_API_KEY is not configured")
        if not destination.get("postal_code"):
            raise ShippingRateUnavailable("Destination postal_code is required")

        rate_items = normalize_rate_items(items)
        destination_postal_code = str(destination["postal_code"])
        base_couriers = settings.biteship_on_demand_couriers if destination_postal_code == settings.store_origin_postal_code else settings.biteship_couriers
        payload = {
            "origin_postal_code": int(settings.store_origin_postal_code),
            "destination_postal_code": int(destination_postal_code),
            "couriers": base_couriers,
            "items": rate_items,
        }
        attempts: list[str] = []
        for rates_payload in build_rate_attempts(payload, destination, settings, api_key):
            attempt_name = str(rates_payload.pop("_attempt"))
            attempts.append(attempt_name)
            try:
                data = post_biteship_rates(rates_payload, settings, api_key)
            except BiteshipNoCourierAvailable:
                continue
            quotes = parse_biteship_quotes(data)
            if quotes:
                return quotes

        raise ShippingRateUnavailable(
            f"Biteship tidak menemukan layanan kurir untuk kode pos {settings.store_origin_postal_code} ke {destination_postal_code}",
            attempts,
        )

def build_rate_attempts(payload: dict[str, object], destination: dict[str, str], settings, api_key: str) -> list[dict[str, object]]:
    attempts: list[dict[str, object]] = [{**payload, "_attempt": "postal_code_primary"}]
    if payload["couriers"] != settings.biteship_expanded_couriers:
        attempts.append({**payload, "couriers": settings.biteship_expanded_couriers, "_attempt": "postal_code_expanded"})
    area_payload = build_area_rate_payload(payload, destination, settings, api_key)
    if area_payload is not None:
        attempts.append({**area_payload, "_attempt": "area_id"})
    return attempts

def build_area_rate_payload(payload: dict[str, object], destination: dict[str, str], settings, api_key: str) -> dict[str, object] | None:
    origin_area_id = settings.store_origin_area_id or resolve_area_id(settings.store_origin_city, settings.store_origin_postal_code, settings, api_key)
    destination_area_id = destination.get("biteship_area_id") or resolve_area_id(destination.get("city"), destination.get("postal_code"), settings, api_key)
    if not origin_area_id or not destination_area_id:
        return None
    return {
        "origin_area_id": origin_area_id,
        "destination_area_id": destination_area_id,
        "couriers": settings.biteship_expanded_couriers,
        "items": payload["items"],
    }

def resolve_area_id(city: str | None, postal_code: str | None, settings, api_key: str) -> str | None:
    query = " ".join(value for value in [city, postal_code] if value)
    if not query:
        return None
    try:
        data = get_biteship_json(
            BITESHIP_AREAS_PATH,
            settings,
            api_key,
            params={"countries": "ID", "input": query, "type": "single"},
        )
    except ShippingRateUnavailable:
        return None
    area = first_area(data)
    if area is None:
        return None
    return area.get("id") or area.get("area_id")

def first_area(payload: dict) -> dict | None:
    areas = payload.get("areas") or payload.get("data") or payload.get("results") or []
    if not isinstance(areas, list) or not areas:
        return None
    area = areas[0]
    return area if isinstance(area, dict) else None

def post_biteship_rates(payload: dict[str, object], settings, api_key: str) -> dict:
    data = post_biteship_json(BITESHIP_RATES_PATH, payload, settings, api_key)
    if is_cloudflare_blocked(data):
        raise BiteshipCloudflareBlocked(data)
    if is_no_courier_available(data):
        raise BiteshipNoCourierAvailable(str(data))
    if data.get("_http_status_code", 200) >= 400:
        raise ShippingRateUnavailable(f"Biteship rates error {data.get('_http_status_code')}: {data}")
    return data

class BiteshipNoCourierAvailable(ShippingRateUnavailable):
    pass

def check_biteship_rates(payload: dict[str, object]) -> dict:
    settings = get_settings()
    api_key = get_biteship_api_key(settings)
    if not api_key or api_key.startswith("change-me"):
        raise ShippingRateUnavailable("BITESHIP_API_KEY is not configured")
    return post_biteship_json(BITESHIP_RATES_PATH, payload, settings, api_key)

def get_biteship_json(path: str, settings, api_key: str, params: dict[str, object] | None = None) -> dict:
    url = biteship_url(settings, path)
    try:
        with httpx.Client(timeout=biteship_timeout(settings), headers=biteship_headers(settings, api_key)) as client:
            response = client.get(url, params=params)
    except httpx.HTTPError as exc:
        raise ShippingRateUnavailable(f"Biteship request failed: {exc}") from exc
    return parse_biteship_response(response)

def post_biteship_json(path: str, payload: dict[str, object], settings, api_key: str) -> dict:
    url = biteship_url(settings, path)
    try:
        with httpx.Client(timeout=biteship_timeout(settings), headers=biteship_headers(settings, api_key)) as client:
            response = client.post(url, json=payload)
    except httpx.HTTPError as exc:
        raise ShippingRateUnavailable(f"Biteship request failed: {exc}") from exc
    return parse_biteship_response(response)

def parse_biteship_response(response: httpx.Response) -> dict:
    try:
        data = response.json()
    except ValueError:
        data = {"success": False, "detail": response.text}
    if isinstance(data, dict):
        data.setdefault("_http_status_code", response.status_code)
        return data
    return {"success": False, "detail": data, "_http_status_code": response.status_code}

def is_cloudflare_blocked(payload: dict) -> bool:
    return bool(payload.get("cloudflare_error")) or (
        payload.get("status") == 403
        and str(payload.get("error_code")) == "1010"
        and payload.get("error_name") == "browser_signature_banned"
    )

def is_no_courier_available(payload: dict | str) -> bool:
    if isinstance(payload, str):
        return "40001010" in payload or "No courier" in payload
    if is_cloudflare_blocked(payload):
        return False
    return str(payload.get("code") or payload.get("error_code") or "") in {"1010", "40001010"}

def get_biteship_api_key(settings) -> str:
    api_key = settings.biteship_api_key.get_secret_value().strip()
    if api_key.lower().startswith("authorization:"):
        api_key = api_key.split(":", 1)[1].strip()
    return api_key

def biteship_headers(settings, api_key: str) -> dict[str, str]:
    return {
        "Authorization": api_key.strip(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": settings.biteship_user_agent.strip(),
    }

def biteship_url(settings, path: str) -> str:
    base_url = settings.biteship_base_url.rstrip("/")
    return f"{base_url}{path}"

def biteship_timeout(settings) -> float:
    return float(settings.biteship_timeout_seconds)

def normalize_rate_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for item in items:
        normalized.append(
            {
                "name": str(item.get("name") or "Product"),
                "value": int(Decimal(str(item.get("value") or "1"))),
                "weight": max(int(item.get("weight") or 1), 1),
                "quantity": max(int(item.get("quantity") or 1), 1),
            }
        )
    return normalized or [{"name": "Cart", "value": 1, "weight": 1, "quantity": 1}]

def parse_biteship_quotes(payload: dict) -> list[dict[str, object]]:
    quotes: list[dict[str, object]] = []
    for item in payload.get("pricing", []):
        price = item.get("price")
        if price is None:
            continue
        quotes.append(
            {
                "courier_code": str(item.get("courier_code") or "biteship"),
                "courier_name": str(item.get("courier_name") or item.get("courier_code") or "Biteship"),
                "service_code": str(item.get("courier_service_code") or item.get("service_code") or "regular"),
                "service_name": str(item.get("courier_service_name") or item.get("service_name") or "Regular"),
                "price": str(Decimal(str(price))),
                "estimated_delivery": item.get("duration") or item.get("shipment_duration_range"),
                "raw_response": item,
            }
        )
    return quotes

def fallback_postal_code_quotes(destination: dict[str, str]) -> list[dict[str, object]]:
    settings = get_settings()
    origin = settings.store_origin_postal_code
    target = destination.get("postal_code") or origin
    distance_km = estimate_postal_code_distance_km(origin, target)
    price = Decimal("10000") + Decimal(min(distance_km, 100)) * Decimal("1500")
    return [
        {
            "courier_code": "estimasi",
            "courier_name": "Estimasi Ongkir",
            "service_code": "kode-pos",
            "service_name": "Estimasi Kode Pos",
            "price": str(price.quantize(Decimal("1"))),
            "estimated_delivery": "estimasi",
            "raw_response": {"source": "postal_code_fallback", "origin": origin, "destination": target},
        }
    ]

def estimate_postal_code_distance_km(origin_postal_code: str, destination_postal_code: str) -> int:
    if origin_postal_code == destination_postal_code:
        return 0
    if origin_postal_code[:2] == destination_postal_code[:2]:
        return max(abs(int(origin_postal_code[-3:]) - int(destination_postal_code[-3:])) // 10, 1)
    return max(abs(int(origin_postal_code[:2]) - int(destination_postal_code[:2])) * 25, 25)
