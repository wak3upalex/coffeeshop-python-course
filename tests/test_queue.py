from app.services.queue import publish_event


class FakeChannel:
    def __init__(self) -> None:
        self.published = []

    def queue_declare(self, queue, durable):
        return None

    def basic_publish(self, exchange, routing_key, body, properties):
        self.published.append(
            {
                "exchange": exchange,
                "routing_key": routing_key,
                "body": body,
                "properties": properties,
            }
        )


class FakeConnection:
    def __init__(self, params):
        self.channel_instance = FakeChannel()

    def channel(self):
        return self.channel_instance

    def close(self):
        return None


def test_publish_event_sends_message(monkeypatch):
    connections = []

    def fake_connection(params):
        conn = FakeConnection(params)
        connections.append(conn)
        return conn

    monkeypatch.setattr("app.services.queue.pika.BlockingConnection", fake_connection)

    publish_event({"type": "order_created", "order_id": 1})

    assert connections
    channel = connections[0].channel_instance
    assert len(channel.published) == 1
