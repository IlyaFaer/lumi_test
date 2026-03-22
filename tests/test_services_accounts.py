from types import SimpleNamespace
import uuid
from unittest.mock import Mock

from services import accounts


def test_create_account(monkeypatch):
    fake_id = uuid.uuid4()

    class AccountMock:
        def __init__(self, name, type):
            self.name = name
            self.type = type
            self.id = fake_id

    monkeypatch.setattr(accounts, "Account", AccountMock)

    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()

    account = SimpleNamespace(name="Cash", type="Asset")
    res = accounts.create_account(session, account)

    assert res["id"] == fake_id
    assert res["name"] == "Cash"
    assert res["type"] == "Asset"
    assert res["balance"] == 0
    session.add.assert_called()
    session.commit.assert_called_once()
    assert isinstance(session.refresh.call_args[0][0], AccountMock)


def test_get_account_by_id():
    session = Mock()
    mapping = {
        "id": uuid.uuid4(),
        "name": "Cash",
        "type": "Asset",
        "balance": 100,
    }
    exec_ret = Mock()
    exec_ret.mappings.return_value.first.return_value = mapping
    session.execute.return_value = exec_ret

    res = accounts.retrieve_account(session, mapping["id"])
    assert res == mapping


def test_list_accounts():
    session = Mock()
    mapping1 = {
        "id": uuid.uuid4(),
        "name": "Cash",
        "type": "Asset",
        "balance": 100,
    }
    mapping2 = {
        "id": uuid.uuid4(),
        "name": "Bank",
        "type": "Asset",
        "balance": 200,
    }

    exec_ret = Mock()
    exec_ret.mappings.return_value.all.return_value = [mapping1, mapping2]
    session.execute.return_value = exec_ret

    res = accounts.list_accounts(session)
    assert res == [mapping1, mapping2]
