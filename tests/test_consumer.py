import json

from app.repositories.orders import OrderRepository
from consumer.main import handle_message


class DummyChannel:
    def __init__(self) -> None:
        self.acked = False
        self.nacked = False

    def basic_ack(self, delivery_tag):
        self.acked = True

    def basic_nack(self, delivery_tag, requeue=False):
        self.nacked = True


class DummyMethod:
    def __init__(self, tag: int = 1) -> None:
        self.delivery_tag = tag


def test_handle_message_processes_order(db_session):
    repo = OrderRepository(db_session)
    order = repo.create(customer_name="Ray", item="Flat White")

    event = {"type": "order_created", "order_id": order.id}
    body = json.dumps(event).encode("utf-8")

    channel = DummyChannel()
    method = DummyMethod()

    handle_message(channel, method, None, body)

    db_session.expire_all()
    updated = repo.get(order.id)
    assert updated is not None
    assert updated.status == "processed"
    assert channel.acked is True


def test_handle_message_ignores_unknown_event(db_session):
    body = json.dumps({"type": "unknown"}).encode("utf-8")
    channel = DummyChannel()
    method = DummyMethod()

    handle_message(channel, method, None, body)

    assert channel.acked is True
    assert channel.nacked is False


def test_handle_message_nacks_on_error():
    channel = DummyChannel()
    method = DummyMethod()

    handle_message(channel, method, None, b"not-json")

    assert channel.nacked is True
