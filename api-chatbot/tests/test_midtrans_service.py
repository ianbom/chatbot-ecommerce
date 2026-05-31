import base64
import json
from types import SimpleNamespace

from pydantic import SecretStr

from app.service import midtrans_service
from app.service.midtrans_service import ConfiguredMidtransClient


class FakeSnapResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(
            {
                "token": "snap-token-test",
                "redirect_url": "https://app.sandbox.midtrans.com/snap/v2/vtweb/snap-token-test",
            }
        ).encode("utf-8")


def test_configured_midtrans_client_creates_snap_transaction(monkeypatch) -> None:
    captured = {}

    monkeypatch.setattr(
        midtrans_service,
        "get_settings",
        lambda: SimpleNamespace(
            midtrans_server_key=SecretStr("server-test"),
            midtrans_is_production=False,
        ),
    )

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["authorization"] = req.get_header("Authorization")
        captured["content_type"] = req.get_header("Content-type")
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return FakeSnapResponse()

    monkeypatch.setattr(midtrans_service.request, "urlopen", fake_urlopen)

    result = ConfiguredMidtransClient().create_payment_link(
        "ORD-TEST-001",
        "610000.00",
        {"phone": "081233914116", "name": "Ian Ale"},
    )

    assert captured["url"] == "https://app.sandbox.midtrans.com/snap/v1/transactions"
    expected_auth = base64.b64encode(b"server-test:").decode("ascii")
    assert captured["authorization"] == f"Basic {expected_auth}"
    assert captured["content_type"] == "application/json"
    assert captured["timeout"] == 30
    assert captured["body"]["transaction_details"] == {
        "order_id": "ORD-TEST-001",
        "gross_amount": 610000,
    }
    assert captured["body"]["customer_details"] == {
        "first_name": "Ian Ale",
        "phone": "081233914116",
    }
    assert result == {
        "provider_order_id": "ORD-TEST-001",
        "payment_url": "https://app.sandbox.midtrans.com/snap/v2/vtweb/snap-token-test",
        "snap_token": "snap-token-test",
        "raw_response": {
            "token": "snap-token-test",
            "redirect_url": "https://app.sandbox.midtrans.com/snap/v2/vtweb/snap-token-test",
        },
    }
