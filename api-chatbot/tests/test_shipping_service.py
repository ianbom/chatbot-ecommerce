from types import SimpleNamespace

from pydantic import SecretStr

from app.service import shipping_service
from app.service.shipping_service import BiteshipShippingClient, ShippingRateUnavailable

def shipping_settings(**overrides) -> SimpleNamespace:
    values = {
        "biteship_api_key": SecretStr("biteship-test-key"),
        "biteship_base_url": "https://api.biteship.com",
        "biteship_user_agent": "chatbot-ecommerce-api/1.0",
        "biteship_timeout_seconds": 30,
        "store_origin_postal_code": "60111",
        "biteship_couriers": "jne,jnt,sicepat,anteraja",
        "biteship_expanded_couriers": "jne,jnt,sicepat,anteraja,pos",
        "biteship_on_demand_couriers": "gojek,grab,paxel",
        "store_origin_city": "Surabaya",
        "store_origin_area_id": "IDNP33IDNC325IDND3713IDZ60111",
    }
    values.update(overrides)
    return SimpleNamespace(**values)

def rates_response() -> dict:
    return {
        "pricing": [
            {
                "courier_code": "jne",
                "courier_name": "JNE",
                "courier_service_code": "reg",
                "courier_service_name": "REG",
                "price": 18000,
                "duration": "2-3 days",
            },
            {
                "courier_code": "jnt",
                "courier_name": "J&T",
                "courier_service_code": "ez",
                "courier_service_name": "EZ",
                "price": 17000,
                "duration": "1-2 days",
            },
        ],
        "_http_status_code": 200,
    }

def test_biteship_headers_include_authorization_and_user_agent() -> None:
    settings = shipping_settings()

    headers = shipping_service.biteship_headers(settings, "biteship-test-key")

    assert headers == {
        "Authorization": "biteship-test-key",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "chatbot-ecommerce-api/1.0",
    }

def test_biteship_shipping_client_requests_rates_by_postal_code(monkeypatch) -> None:
    captured = {}
    monkeypatch.setattr(shipping_service, "get_settings", shipping_settings)

    def fake_post(path, payload, settings, api_key):
        captured["path"] = path
        captured["payload"] = payload
        captured["api_key"] = api_key
        return rates_response()

    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    quotes = BiteshipShippingClient().get_shipping_quotes(
        {"postal_code": "50158"},
        [{"name": "Hoodie Black L", "value": 249000, "weight": 600, "quantity": 2}],
    )

    assert captured["path"] == "/v1/rates/couriers"
    assert captured["api_key"] == "biteship-test-key"
    assert captured["payload"] == {
        "origin_postal_code": 60111,
        "destination_postal_code": 50158,
        "couriers": "jne,jnt,sicepat,anteraja",
        "items": [{"name": "Hoodie Black L", "value": 249000, "weight": 600, "quantity": 2}],
    }
    assert quotes[0]["courier_code"] == "jne"
    assert quotes[1]["courier_code"] == "jnt"
    assert quotes[1]["price"] == "17000"

def test_biteship_shipping_client_raises_when_rates_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        shipping_service,
        "get_settings",
        lambda: shipping_settings(biteship_api_key=SecretStr("change-me-biteship-api-key")),
    )

    try:
        BiteshipShippingClient().get_shipping_quotes({"postal_code": "50158"}, [])
    except ShippingRateUnavailable as exc:
        assert "BITESHIP_API_KEY" in str(exc)
    else:
        raise AssertionError("ShippingRateUnavailable was not raised")

def test_biteship_shipping_client_retries_with_expanded_couriers_for_no_courier_error(monkeypatch) -> None:
    captured_payloads = []
    monkeypatch.setattr(
        shipping_service,
        "get_settings",
        lambda: shipping_settings(biteship_couriers="jne,jnt", biteship_expanded_couriers="jne,jnt,pos"),
    )

    def fake_post(path, payload, settings, api_key):
        captured_payloads.append(payload)
        if len(captured_payloads) == 1:
            return {"success": False, "code": 40001010, "error": "No courier available", "_http_status_code": 400}
        return rates_response()

    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    quotes = BiteshipShippingClient().get_shipping_quotes(
        {"postal_code": "50158"},
        [{"name": "Hoodie Black L", "value": 249000, "weight": 600, "quantity": 1}],
    )

    assert len(captured_payloads) == 2
    assert captured_payloads[0]["couriers"] == "jne,jnt"
    assert captured_payloads[1]["couriers"] == "jne,jnt,pos"
    assert quotes[0]["courier_code"] == "jne"

def test_biteship_shipping_client_uses_on_demand_couriers_for_same_postal_code(monkeypatch) -> None:
    captured_payloads = []
    monkeypatch.setattr(
        shipping_service,
        "get_settings",
        lambda: shipping_settings(biteship_couriers="jne,jnt", biteship_on_demand_couriers="gojek,grab,paxel"),
    )

    def fake_post(path, payload, settings, api_key):
        captured_payloads.append(payload)
        return rates_response()

    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    quotes = BiteshipShippingClient().get_shipping_quotes(
        {"city": "Surabaya", "postal_code": "60111"},
        [{"name": "Baju Lebaran", "value": 600000, "weight": 100, "quantity": 1}],
    )

    assert captured_payloads[0]["couriers"] == "gojek,grab,paxel"
    assert captured_payloads[0]["origin_postal_code"] == 60111
    assert captured_payloads[0]["destination_postal_code"] == 60111
    assert quotes[0]["courier_code"] == "jne"

def test_biteship_shipping_client_retries_with_area_id_after_postal_code_failures(monkeypatch) -> None:
    captured_rate_payloads = []
    captured_area_params = []
    monkeypatch.setattr(
        shipping_service,
        "get_settings",
        lambda: shipping_settings(biteship_couriers="jne,jnt", biteship_expanded_couriers="jne,jnt,pos"),
    )

    def fake_get(path, settings, api_key, params=None):
        captured_area_params.append(params)
        return {"areas": [{"id": "IDNP33IDNC325IDND3713IDZ60112", "name": "Surabaya", "postal_code": "60112"}]}

    def fake_post(path, payload, settings, api_key):
        captured_rate_payloads.append(payload)
        if len(captured_rate_payloads) < 3:
            return {"success": False, "code": 40001010, "error": "No courier available", "_http_status_code": 400}
        return rates_response()

    monkeypatch.setattr(shipping_service, "get_biteship_json", fake_get)
    monkeypatch.setattr(shipping_service, "post_biteship_json", fake_post)

    quotes = BiteshipShippingClient().get_shipping_quotes(
        {"city": "Surabaya", "postal_code": "60112"},
        [{"name": "Baju Lebaran", "value": 600000, "weight": 100, "quantity": 1}],
    )

    assert len(captured_rate_payloads) == 3
    assert captured_rate_payloads[2]["origin_area_id"] == "IDNP33IDNC325IDND3713IDZ60111"
    assert captured_rate_payloads[2]["destination_area_id"] == "IDNP33IDNC325IDND3713IDZ60112"
    assert "origin_postal_code" not in captured_rate_payloads[2]
    assert captured_area_params
    assert quotes[0]["courier_code"] == "jne"
