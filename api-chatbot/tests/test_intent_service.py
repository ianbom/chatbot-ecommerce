from app.service.intent_service import parse_customer_message

def test_waiting_shipping_confirmation_accepts_plain_number_selection() -> None:
    parsed = parse_customer_message(
        "3",
        chat_history="",
        state={"stage": "waiting_shipping_confirmation", "current_product_id": 1},
        llm_client=None,
    )

    assert parsed.intent == "create_payment"
    assert parsed.quantity == 3

def test_waiting_shipping_confirmation_accepts_number_with_courier_text() -> None:
    parsed = parse_customer_message(
        "3. JNE Yakin Esok Sampai",
        chat_history="",
        state={"stage": "waiting_shipping_confirmation", "current_product_id": 1},
        llm_client=None,
    )

    assert parsed.intent == "create_payment"
    assert parsed.quantity == 3
