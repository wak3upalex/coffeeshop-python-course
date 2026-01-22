from app.models.order import Order
from app.repositories.orders import OrderRepository
from app.services.events import order_created_event
from app.services.queue import publish_event
from sqlalchemy.orm import Session


class OrderService:
    """Класс операций с заказами.

    Инкапсулирует бизнес-логику и взаимодействие с репозиторием
    и очередью событий.
    """

    def __init__(self, db: Session) -> None:
        """Инициализирует сервис с сессией БД.
        Args:
            db (Session): SQLAlchemy сессия.
        """
        self.repo = OrderRepository(db)

    def create_order(self, customer_name: str, item: str) -> Order:
        """Создает заказ и публикует событие в очередь.
        Args:
            customer_name (str): Имя клиента.
            item (str): Название позиции.

        Returns:
            Order: Созданный заказ.
        """
        order = self.repo.create(customer_name=customer_name, item=item)
        publish_event(order_created_event(order))
        return order

    def get_order(self, order_id: int) -> Order | None:
        """Возвращает заказ по идентификатору.

        Args:
            order_id: Идентификатор заказа.

        Returns:
            Order | None: Заказ или None, если не найден.
        """
        return self.repo.get(order_id)

    def list_orders(self) -> list[Order]:
        """Возвращает список всех заказов.

        Returns:
            list[Order]: Список заказов.
        """
        return self.repo.list()
