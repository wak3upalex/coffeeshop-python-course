class OrderNotFoundError(Exception):
    """Ошибка в случае отсутствия заказа

    Attributes:
        order_id (int): Идентификатор заказа, который не найден.
    """

    def __init__(self, order_id: int) -> None:
        super().__init__(f"Order {order_id} not found")
        self.order_id = order_id
