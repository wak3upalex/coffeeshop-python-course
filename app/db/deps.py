from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Создаёт и отдаёт сессию БД для зависимостей FastAPI.

    Сессия создаётся на каждый запрос и закрывается после использования
    Returns:
        Generator[Session, None, None]: Сессия `sql-alchemy`, привязанная к запросу
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
