from app.services.errors import OrderNotFoundError
from app.services.orders import OrderService


def test_order_service_get_and_list(db_session):
    service = OrderService(db_session)
    assert service.list_orders() == []
    assert service.get_order(order_id=999) is None


def test_order_not_found_error_message():
    err = OrderNotFoundError(42)
    assert "42" in str(err)
