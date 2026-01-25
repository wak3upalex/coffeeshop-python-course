import os
import tempfile

import pytest
from fastapi.testclient import TestClient

_db_dir = tempfile.mkdtemp(prefix="coffeeshop-test-")
_db_path = os.path.join(_db_dir, "test.db")

if "COFFEE_DATABASE_URL" not in os.environ:
    os.environ["COFFEE_DATABASE_URL"] = f"sqlite:///{_db_path}"
if "COFFEE_RABBITMQ_URL" not in os.environ:
    os.environ["COFFEE_RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"
if "COFFEE_RABBITMQ_QUEUE" not in os.environ:
    os.environ["COFFEE_RABBITMQ_QUEUE"] = "orders"


def _prepare_database() -> None:
    from app.db.base import Base
    from app.db.session import engine

    Base.metadata.create_all(bind=engine)


def _drop_database() -> None:
    from app.db.base import Base
    from app.db.session import engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    from app.db.session import SessionLocal

    _prepare_database()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        _drop_database()


@pytest.fixture()
def client(db_session):
    from app.db.deps import get_db
    from app.main import app

    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
