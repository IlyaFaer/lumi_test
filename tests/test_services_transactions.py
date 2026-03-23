import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import uuid

import pytest

from services import transactions


class TestTransactionValidation:
    def test__validate_entries(self):
        entries = [
            SimpleNamespace(type="DEBIT", amount=100),
            SimpleNamespace(type="CREDIT", amount=100),
        ]
        # should not raise
        transactions._validate_entries(entries)

    def test__validate_entries_imbalance(self):
        entries = [
            SimpleNamespace(type="DEBIT", amount=100),
            SimpleNamespace(type="CREDIT", amount=50),
        ]
        with pytest.raises(Exception) as exc:
            transactions._validate_entries(entries)

        assert "amounts must be equal" in str(exc.value)

    def test_entries_not_even(self, client):
        entries = [
            SimpleNamespace(type="DEBIT", amount=100),
            SimpleNamespace(type="DEBIT", amount=70),
        ]
        with pytest.raises(Exception) as exc:
            transactions._validate_entries(entries)

        assert "at least one DEBIT" in str(exc.value)


def test_create_transaction(monkeypatch):
    fake_id = uuid.uuid4()

    class TransactionMock:
        def __init__(self, description, timestamp):
            self.description = description
            self.timestamp = timestamp
            self.id = fake_id

    class EntryMock:
        def __init__(self, transaction_id, account_id, type, amount):
            self.transaction_id = transaction_id
            self.account_id = account_id
            self.type = type
            self.amount = amount

    monkeypatch.setattr(transactions, "Transaction", TransactionMock)
    monkeypatch.setattr(transactions, "TransactionEntry", EntryMock)

    session = Mock()

    def _add_side_effect(obj):
        """
        SQLAlchemy will try to re-read the data and will drop our test id.
        The side effect prevents it.
        """
        if not getattr(obj, "id", None):
            obj.id = fake_id

    session.add = Mock(side_effect=_add_side_effect)
    session.commit = Mock()
    session.refresh = Mock()

    transaction_raw = SimpleNamespace(
        description="desc",
        date="2023-01-01",
        entries=[
            SimpleNamespace(accountId="a1", type="DEBIT", amount=100),
            SimpleNamespace(accountId="a2", type="CREDIT", amount=100),
        ],
    )

    fake_return = TransactionMock(
        transaction_raw.description,
        transaction_raw.date,
    )

    def get_transaction_by_id_mock(s, tid):
        s.refresh(fake_return)
        return fake_return

    monkeypatch.setattr(
        transactions, "retrieve_transaction", get_transaction_by_id_mock
    )


def test_get_transaction_by_id():
    session = Mock()
    ts = datetime.datetime(2023, 1, 1, 12, 0)
    tx_row = {"id": "tx-1", "timestamp": ts, "description": "desc"}
    entry_row = {"account_id": "a1", "type": "DEBIT", "amount": 100}

    exec_ret = Mock()
    exec_ret.mappings.return_value.first.return_value = tx_row

    exec_ret2 = Mock()
    exec_ret2.mappings.return_value.all.return_value = [entry_row]

    session.execute.side_effect = [exec_ret, exec_ret2]

    res = transactions.retrieve_transaction(session, "tx-1")
    assert res["id"] == "tx-1"
    assert res["description"] == "desc"
    assert res["date"] == ts.isoformat()
    assert isinstance(res["entries"], list)
    assert res["entries"][0]["account_id"] == "a1"


def test_list_transactions_by_account_id():
    session = Mock()
    ts = datetime.datetime(2023, 1, 1, 12, 0)

    rows = [
        {
            "id": "e1",
            "account_id": "a1",
            "type": "DEBIT",
            "amount": 100,
            "transaction_id": "tx1",
            "date": ts,
            "description": "t1",
        },
        {
            "id": "e2",
            "account_id": "a1",
            "type": "CREDIT",
            "amount": 50,
            "transaction_id": "tx2",
            "date": ts,
            "description": "t2",
        },
    ]

    exec_ret = Mock()
    exec_ret.mappings.return_value.all.return_value = rows
    session.execute.return_value = exec_ret

    res = transactions.list_transactions_by_account_id(session, "a1")
    assert any(tx["id"] == "tx1" for tx in res)
    assert any(tx["id"] == "tx2" for tx in res)
    for tx in res:
        assert "entries" in tx and isinstance(tx["entries"], list)
