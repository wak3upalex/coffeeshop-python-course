from app.models.order import Order
from app.services.events import order_created_event


def test_order_created_event_fields():
    order = Order(id=1, customer_name="Alex", item="Latte")
    event = order_created_event(order)

    assert event["type"] == "order_created"
    assert event["order_id"] == 1
    assert event["customer_name"] == "Alex"
    assert event["item"] == "Latte"
