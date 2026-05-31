from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.main import app
from app.service import shipping_service

client = TestClient(app)

def fake_settings() -> SimpleNamespace:
    return SimpleNamespace(
        biteship_api_key=SecretStr("biteship-test-key"),
        biteship_base_url="https://api.biteship.com",
        biteship_user_agent="chatbot-ecommerce-api/1.0",
        biteship_timeout_seconds=30,
    )

def test_check_shipping_rates_posts_payload_to_biteship(monkeypatch) -> None:
    captured = {}

    def fake_post(path, payload, settings, api_key):
        captured["path"] = path
        captured["payload"] = payload
        captured["api_key"] = api_key
        captured["user_agent"] = settings.biteship_user_agent
        return {"success": True, "pricing": [{"courier_code": "jne", "price": 18000}], "_http_status_code": 200}

    monkeypatch.setattr(shipping_service, "get_settings", fake_settings)
    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    payload = {
        "origin_postal_code": 12440,
        "destination_postal_code": 12240,
        "couriers": "anteraja,jne,sicepat",
        "items": [
            {
                "name": "Shoes",
                "description": "Black colored size 45",
                "value": 199000,
                "length": 30,
                "width": 15,
                "height": 20,
                "weight": 200,
                "quantity": 2,
            }
        ],
    }

    response = client.post("/api/shipping/rates/check", json=payload)

    assert response.status_code == 200
    assert response.json() == {"success": True, "pricing": [{"courier_code": "jne", "price": 18000}]}
    assert captured == {
        "path": "/v1/rates/couriers",
        "payload": payload,
        "api_key": "biteship-test-key",
        "user_agent": "chatbot-ecommerce-api/1.0",
    }

def test_check_shipping_rates_returns_biteship_error_body_for_debugging(monkeypatch) -> None:
    def fake_post(path, payload, settings, api_key):
        return {"success": False, "code": 40001010, "error": "No courier available", "_http_status_code": 400}

    monkeypatch.setattr(shipping_service, "get_settings", fake_settings)
    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    response = client.post(
        "/api/shipping/rates/check",
        json={
            "origin_postal_code": 60111,
            "destination_postal_code": 60112,
            "couriers": "ninja,sap",
            "items": [{"name": "Book", "value": 149000, "weight": 1000, "quantity": 1}],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"success": False, "code": 40001010, "error": "No courier available"}

def test_check_shipping_rates_returns_clear_cloudflare_error(monkeypatch) -> None:
    cloudflare_body = {
        "status": 403,
        "error_code": 1010,
        "error_name": "browser_signature_banned",
        "cloudflare_error": True,
        "_http_status_code": 403,
    }

    def fake_post(path, payload, settings, api_key):
        return cloudflare_body

    monkeypatch.setattr(shipping_service, "get_settings", fake_settings)
    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    response = client.post(
        "/api/shipping/rates/check",
        json={
            "origin_postal_code": 60111,
            "destination_postal_code": 60112,
            "couriers": "ninja,sap",
            "items": [{"name": "Book", "value": 149000, "weight": 1000, "quantity": 1}],
        },
    )

    assert response.status_code == 403
    assert "Biteship request blocked by Cloudflare" in response.json()["detail"]
    assert response.json()["biteship_error"] == {
        "status": 403,
        "error_code": 1010,
        "error_name": "browser_signature_banned",
        "cloudflare_error": True,
    }
