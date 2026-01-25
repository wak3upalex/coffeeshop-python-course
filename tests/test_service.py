from app.services.orders import OrderService


def test_order_service_creates_and_publishes(db_session, monkeypatch):
    calls = []

    def fake_publish(event: dict) -> None:
        calls.append(event)

    monkeypatch.setattr("app.services.orders.publish_event", fake_publish)

    service = OrderService(db_session)
    order = service.create_order(customer_name="Lee", item="Cappuccino")

    assert order.id is not None
    assert calls
    assert calls[0]["order_id"] == order.id
