from app.repositories.orders import OrderRepository


def test_order_repository_crud(db_session):
    repo = OrderRepository(db_session)

    created = repo.create(customer_name="Sam", item="Espresso")
    assert created.id is not None
    assert created.status == "created"

    fetched = repo.get(created.id)
    assert fetched is not None
    assert fetched.customer_name == "Sam"

    listed = repo.list()
    assert len(listed) == 1
    assert listed[0].id == created.id

    updated = repo.update_status(created.id, "processed")
    assert updated is not None
    assert updated.status == "processed"


def test_update_status_missing_returns_none(db_session):
    repo = OrderRepository(db_session)
    assert repo.update_status(999, "processed") is None
