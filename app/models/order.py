from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
    """ORM-модель заказаю

    Хранятся данные о заказе, его статусе и времени создания.

    Attributes:
        id (int): Уникальный идентификатор заказа.
        customer_name (str): Имя клиента, оформившего заказ.
        item (str): Название позиции заказа.
        status (str): Текущий статус заказа. По умолчанию "created".
        created_at (datetime): Дата и время создания заказа.
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
