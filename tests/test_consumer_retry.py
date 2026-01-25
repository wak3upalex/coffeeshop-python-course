import pytest
from pika.exceptions import AMQPConnectionError

from consumer.main import _connect_with_retry


def test_connect_with_retry_succeeds(monkeypatch):
    calls = {"count": 0}

    def fake_connection(params):
        calls["count"] += 1
        if calls["count"] == 1:
            raise AMQPConnectionError
        return object()

    monkeypatch.setattr("consumer.main.pika.BlockingConnection", fake_connection)
    monkeypatch.setattr("consumer.main.time.sleep", lambda _: None)

    connection = _connect_with_retry(max_attempts=2, delay_seconds=0)
    assert connection is not None


def test_connect_with_retry_fails(monkeypatch):
    def fake_connection(params):
        raise AMQPConnectionError

    monkeypatch.setattr("consumer.main.pika.BlockingConnection", fake_connection)
    monkeypatch.setattr("consumer.main.time.sleep", lambda _: None)

    with pytest.raises(AMQPConnectionError):
        _connect_with_retry(max_attempts=2, delay_seconds=0)
