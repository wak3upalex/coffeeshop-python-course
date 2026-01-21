from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    customer_name: str
    item: str


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    item: str
    status: str
    created_at: datetime
