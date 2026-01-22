import json
import logging

import pika

from app.core.config import settings

logger = logging.getLogger(__name__)


def publish_event(event: dict) -> None:
    """Публикует событие в очередь RabbitMQ.

    Устанавливает подключение, объявляет очередь и отправляет
    сообщение в формате JSON.
    Args:
        event (dict): Словарь с данными события.
    """
    connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
    body = json.dumps(event).encode("utf-8")
    channel.basic_publish(
        exchange="",
        routing_key=settings.rabbitmq_queue,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()
    logger.info("Published event to queue", extra={"event_type": event.get("type")})
