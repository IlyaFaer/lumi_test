from datetime import datetime
from decimal import Decimal

from .conftest import client


def test_account_create(client):
    r = client.post("/accounts/", json={"name": "Cash", "type": "ASSET"})
    assert r.status_code == 201

    data = r.json()
    assert data["name"] == "Cash"
    assert data["type"] == "ASSET"
    assert Decimal(str(data["balance"])) == Decimal("0")


def test_transaction_create_and_retrieve(client):
    r1 = client.post("/accounts/", json={"name": "A1", "type": "ASSET"})
    r2 = client.post("/accounts/", json={"name": "A2", "type": "LIABILITY"})
    a1 = r1.json()["id"]
    a2 = r2.json()["id"]

    payload = {
        "description": "initial",
        "date": "2026-03-05T00:00:00Z",
        "entries": [
            {"accountId": a1, "amount": 100.0, "type": "DEBIT"},
            {"accountId": a2, "amount": 100.0, "type": "CREDIT"},
        ],
    }
    r = client.post("/transactions/", json=payload)
    assert r.status_code == 201

    tx = r.json()
    tx_id = tx["id"]

    got = client.get(f"/transactions/{tx_id}")
    assert got.status_code == 200

    data = got.json()
    assert data["id"] == tx_id
    assert isinstance(data["entries"], list)
    assert sum(e["amount"] for e in data["entries"]) == 200


def test_unbalanced_transaction(client):
    r1 = client.post("/accounts/", json={"name": "B1", "type": "ASSET"})
    r2 = client.post("/accounts/", json={"name": "B2", "type": "LIABILITY"})
    payload = {
        "entries": [
            {"accountId": r1.json()["id"], "amount": 100.0, "type": "DEBIT"},
            {"accountId": r2.json()["id"], "amount": 50.0, "type": "CREDIT"},
        ]
    }
    r = client.post("/transactions/", json=payload)
    assert r.status_code == 400
    assert "Total DEBIT and CREDIT" in r.json().get("detail", "")


def test_balance_multiple_transactions(client):
    ra = client.post("/accounts/", json={"name": "AssetAcct", "type": "ASSET"})
    rb = client.post("/accounts/", json={"name": "LiabAcct", "type": "LIABILITY"})
    a = ra.json()["id"]
    b = rb.json()["id"]

    client.post(
        "/transactions/",
        json={
            "description": "desc",
            "timestamp": datetime(2026, 12, 12).isoformat(),
            "entries": [
                {"accountId": a, "amount": 100.0, "type": "DEBIT"},
                {"accountId": b, "amount": 100.0, "type": "CREDIT"},
            ],
        },
    )
    client.post(
        "/transactions/",
        json={
            "description": "desc",
            "timestamp": datetime(2026, 12, 12).isoformat(),
            "entries": [
                {"accountId": b, "amount": 25.0, "type": "DEBIT"},
                {"accountId": a, "amount": 25.0, "type": "CREDIT"},
            ],
        },
    )

    ga = client.get(f"/accounts/{a}")
    gb = client.get(f"/accounts/{b}")
    assert ga.status_code == 200
    assert gb.status_code == 200

    bal_a = Decimal(str(ga.json()["balance"]))
    bal_b = Decimal(str(gb.json()["balance"]))
    assert bal_a == Decimal("75")
    assert bal_b == Decimal("75")
