import logging

from fastapi import FastAPI

from app.api.orders import router as orders_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name)
app.include_router(orders_router)
