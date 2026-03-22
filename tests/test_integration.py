from datetime import datetime
from decimal import Decimal

from .conftest import client


class TestAccountCreate:
    def test_correct_account(self, client):
        r = client.post("/api/accounts/", json={"name": "Cash", "type": "ASSET"})
        assert r.status_code == 201

        data = r.json()
        assert data["name"] == "Cash"
        assert data["type"] == "ASSET"
        assert Decimal(str(data["balance"])) == Decimal("0")

    def test_invalid_type(self, client):
        r = client.post("/api/accounts/", json={"name": "Invalid", "type": "UNKNOWN"})
        assert r.status_code == 422

    def test_empty_name(self, client):
        r = client.post("/api/accounts/", json={"name": "", "type": "ASSET"})
        assert r.status_code == 422

    def test_repeated_name(self, client):
        r1 = client.post("/api/accounts/", json={"name": "Duplicate", "type": "ASSET"})
        assert r1.status_code == 201

        r2 = client.post(
            "/api/accounts/", json={"name": "Duplicate", "type": "LIABILITY"}
        )
        assert r2.status_code == 409
        assert "already exists" in r2.json().get("detail", "")


class TestTransaction:
    def test_create_account_not_found(self, client):
        payload = {
            "description": "desc" * 10,
            "date": "2026-03-05T00:00:00Z",
            "entries": [
                {
                    "accountId": "00000000-0000-0000-0000-000000000000",
                    "amount": 100.0,
                    "type": "DEBIT",
                },
                {
                    "accountId": "00000000-0000-0000-0000-000000000001",
                    "amount": 100.0,
                    "type": "CREDIT",
                },
            ],
        }
        r = client.post("/api/transactions/", json=payload)
        assert r.status_code == 404
        assert "not found" in r.json().get("detail", "")

    def test_create_negative_sum(self, client):
        r1 = client.post("/api/accounts/", json={"name": "Neg1", "type": "ASSET"})
        r2 = client.post("/api/accounts/", json={"name": "Neg2", "type": "LIABILITY"})

        payload = {
            "description": "desc" * 10,
            "date": "2026-03-05T00:00:00Z",
            "entries": [
                {"accountId": r1.json()["id"], "amount": -100.0, "type": "DEBIT"},
                {"accountId": r2.json()["id"], "amount": -100.0, "type": "CREDIT"},
            ],
        }
        r = client.post("/api/transactions/", json=payload)
        assert r.status_code == 422

    def test_credit_and_debit_mismatch(self, client):
        payload = {
            "description": "desc" * 10,
            "date": "2026-03-05T00:00:00Z",
            "entries": [
                {
                    "accountId": "00000000-0000-0000-0000-000000000000",
                    "amount": 80.0,
                    "type": "DEBIT",
                },
                {
                    "accountId": "00000000-0000-0000-0000-000000000001",
                    "amount": 100.0,
                    "type": "CREDIT",
                },
            ],
        }
        r = client.post("/api/transactions/", json=payload)
        assert r.status_code == 400
        assert "must be equal" in r.json().get("detail", "")

    def test_entries_not_even(self, client):
        payload = {
            "description": "desc" * 10,
            "date": "2026-03-05T00:00:00Z",
            "entries": [
                {
                    "accountId": "00000000-0000-0000-0000-000000000000",
                    "amount": 80.0,
                    "type": "DEBIT",
                },
                {
                    "accountId": "00000000-0000-0000-0000-000000000001",
                    "amount": 70.0,
                    "type": "DEBIT",
                },
            ],
        }
        r = client.post("api/transactions/", json=payload)
        assert r.status_code == 400
        assert "at least one DEBIT and one CREDIT" in r.json().get("detail", "")

    def test_create_and_retrieve(self, client):
        r1 = client.post("/api/accounts/", json={"name": "A1", "type": "ASSET"})
        r2 = client.post("/api/accounts/", json={"name": "A2", "type": "LIABILITY"})
        a1 = r1.json()["id"]
        a2 = r2.json()["id"]

        payload = {
            "description": "desc" * 10,
            "date": "2026-03-05T00:00:00Z",
            "entries": [
                {"accountId": a1, "amount": 100.0, "type": "DEBIT"},
                {"accountId": a2, "amount": 100.0, "type": "CREDIT"},
            ],
        }
        r = client.post("/api/transactions/", json=payload)
        assert r.status_code == 201

        tx = r.json()
        tx_id = tx["id"]

        got = client.get(f"/api/transactions/{tx_id}")
        assert got.status_code == 200

        data = got.json()
        assert data["id"] == tx_id
        assert isinstance(data["entries"], list)
        assert sum(Decimal(e["amount"]) for e in data["entries"]) == 200

    def test_unbalanced_transaction(self, client):
        r1 = client.post("/api/accounts/", json={"name": "B1", "type": "ASSET"})
        r2 = client.post("/api/accounts/", json={"name": "B2", "type": "LIABILITY"})
        payload = {
            "description": "desc" * 10,
            "entries": [
                {"accountId": r1.json()["id"], "amount": 100.0, "type": "DEBIT"},
                {"accountId": r2.json()["id"], "amount": 50.0, "type": "CREDIT"},
            ],
        }
        r = client.post("/api/transactions/", json=payload)
        assert r.status_code == 400
        assert "Total DEBIT and CREDIT" in r.json().get("detail", "")

    def test_balance_multiple_transactions(self, client):
        ra = client.post("/api/accounts/", json={"name": "AssetAcct", "type": "ASSET"})
        rb = client.post(
            "/api/accounts/", json={"name": "LiabAcct", "type": "LIABILITY"}
        )
        a = ra.json()["id"]
        b = rb.json()["id"]

        client.post(
            "/api/transactions/",
            json={
                "description": "desc" * 10,
                "timestamp": datetime(2026, 12, 12).isoformat(),
                "entries": [
                    {"accountId": a, "amount": 100.0, "type": "DEBIT"},
                    {"accountId": b, "amount": 100.0, "type": "CREDIT"},
                ],
            },
        )
        client.post(
            "/api/transactions/",
            json={
                "description": "desc" * 10,
                "timestamp": datetime(2026, 12, 12).isoformat(),
                "entries": [
                    {"accountId": b, "amount": 25.0, "type": "DEBIT"},
                    {"accountId": a, "amount": 25.0, "type": "CREDIT"},
                ],
            },
        )

        ga = client.get(f"/api/accounts/{a}")
        gb = client.get(f"/api/accounts/{b}")
        assert ga.status_code == 200
        assert gb.status_code == 200

        bal_a = Decimal(str(ga.json()["balance"]))
        bal_b = Decimal(str(gb.json()["balance"]))
        assert bal_a == Decimal("75")
        assert bal_b == Decimal("75")
