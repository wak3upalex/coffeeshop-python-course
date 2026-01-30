from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    """Репозиторий для работы с заказами.

    Инкапсуляция CRUD операций для Order на уровне базы данных (БД).

    Args:
        db (Session): Активная сессия SQLAlchemy
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, customer_name: str, item: str) -> Order:
        """Создаёт заказ и сохраняет в БД.

        Args:
            customer_name: имя клиента
            item: нащвание позиции.

        Returns:
            Order: созданный заказ с заполненным идентификатором

        """
        order = Order(customer_name=customer_name, item=item)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get(self, order_id: int) -> Order | None:
        """Возвращает заказ по идентификатору.

        Args:
            order_id: Идентификатор заказа.

        Returns:
            Order | None: Заказ или None, если не найден.

        """
        return self.db.get(Order, order_id)

    def list(self) -> list[Order]:
        """Возаращает список заказов, отсортированных, по id.

        Returns:
            list[Order]: список заказов

        """
        result = self.db.execute(select(Order).order_by(Order.id))
        return list(result.scalars().all())

    def update_status(self, order_id: int, status: str) -> Order | None:
        """Обновляет статус заказа.

        Args:
            order_id: идентификатор заказа
            status: новый статус

        Returns:
            Order | None: Обновлённый заказ, либо None, если не найден
        """
        order = self.get(order_id)
        if order is None:
            return None
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order
