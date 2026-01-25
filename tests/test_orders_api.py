def test_create_order(client, monkeypatch):
    monkeypatch.setattr("app.services.orders.publish_event", lambda event: None)
    response = client.post("/orders", json={"customer_name": "Nina", "item": "Mocha"})

    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Nina"
    assert data["status"] == "created"


def test_get_order_not_found(client):
    response = client.get("/orders/999")
    assert response.status_code == 404


def test_list_orders(client, monkeypatch):
    monkeypatch.setattr("app.services.orders.publish_event", lambda event: None)
    client.post("/orders", json={"customer_name": "Nina", "item": "Mocha"})
    response = client.get("/orders")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
