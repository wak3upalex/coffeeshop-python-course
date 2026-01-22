from app.models.order import Order


def order_created_event(order: Order) -> dict:
    """Формирование события о создании заказа

    Args:
        order (Order): ORM-модель созданного заказа.

    Returns:
        dict: Событие в формате с полями заказа.
    """
    return {
        "type": "order_created",
        "order_id": order.id,
        "customer_name": order.customer_name,
        "item": order.item,
    }
