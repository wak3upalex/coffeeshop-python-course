import json
import logging
import time

import pika

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.orders import OrderRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_message(channel, method, properties, body) -> None:
    """Обрабатывает сообщение из очереди.

    Принимает события `order_created`, обновляет статус заказа и подтверждает
    сообщение. Для неизвестных событий делает ack без обработки.

    Args:
        channel: Канал RabbitMQ.
        method: Метаданные доставки сообщения.
        properties: Свойства сообщения.
        body: Тело сообщения в байтах.

    Raises:
        Exception: Любая ошибка приводит к nack без requeue.
    """
    try:
        event = json.loads(body)
        if event.get("type") != "order_created":
            logger.info("Ignoring event", extra={"event_type": event.get("type")})
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return
        order_id = int(event["order_id"])
        with SessionLocal() as db:
            repo = OrderRepository(db)
            updated = repo.update_status(order_id, "processed")
        logger.info(
            "Processed order event",
            extra={"order_id": order_id, "updated": bool(updated)},
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("Failed to process message")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def _connect_with_retry(
    max_attempts: int = 10, delay_seconds: int = 3
) -> pika.BlockingConnection:
    """Пытается подключиться к RabbitMQ с повторными попытками.

    Args:
        max_attempts (int): Максимальное число попыток.
        delay_seconds (int): Задержка между попытками в секундах.
    Returns:
        pika.BlockingConnection: Установленное соединение.
    Raises:
        pika.exceptions.AMQPConnectionError: Если подключение не удалось.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
        except pika.exceptions.AMQPConnectionError:
            logger.info("RabbitMQ not ready, retrying", extra={"attempt": attempt})
            time.sleep(delay_seconds)
    raise pika.exceptions.AMQPConnectionError("Unable to connect to RabbitMQ")


def main() -> None:
    """Запускает consumer и начинает обработку сообщений."""
    connection = _connect_with_retry()
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.rabbitmq_queue, on_message_callback=handle_message
    )
    logger.info("Consumer started")
    channel.start_consuming()


if __name__ == "__main__":
    main()
