from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.order import OrderCreate, OrderRead
from app.services.orders import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate, db: Annotated[Session, Depends(get_db)]
) -> OrderRead:
    service = OrderService(db)
    order = service.create_order(customer_name=payload.customer_name, item=payload.item)
    return OrderRead.model_validate(order)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Annotated[Session, Depends(get_db)]) -> OrderRead:
    service = OrderService(db)
    order = service.get_order(order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead.model_validate(order)


@router.get("", response_model=list[OrderRead])
def list_orders(db: Annotated[Session, Depends(get_db)]) -> list[OrderRead]:
    service = OrderService(db)
    return [OrderRead.model_validate(order) for order in service.list_orders()]
