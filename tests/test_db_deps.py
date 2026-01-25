from sqlalchemy.orm import Session

from app.db.deps import get_db


def test_get_db_yields_session():
    generator = get_db()
    db = next(generator)
    assert isinstance(db, Session)
    generator.close()
