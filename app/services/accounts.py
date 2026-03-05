from db.accounts import Account, AccountType
from db.transactions import TransactionEntry, TransactionType
from sqlalchemy import case, func, select


class BalanceQueryBuilder:
    def __init__(self):
        self._query = None

    @property
    def query(self):
        return self._query

    def select_case(self):
        asset_or_expense = Account.type.in_(
            [
                AccountType.Asset,
                AccountType.Expenses,
            ]
        )
        liability_or_revenue = Account.type.in_(
            [
                AccountType.Liability,
                AccountType.Revenue,
            ]
        )

        return case(
            (
                asset_or_expense & (TransactionEntry.type == TransactionType.Debit),
                TransactionEntry.amount,
            ),
            (
                asset_or_expense & (TransactionEntry.type == TransactionType.Credit),
                -TransactionEntry.amount,
            ),
            (
                liability_or_revenue & (TransactionEntry.type == TransactionType.Debit),
                -TransactionEntry.amount,
            ),
            (
                liability_or_revenue
                & (TransactionEntry.type == TransactionType.Credit),
                TransactionEntry.amount,
            ),
            else_=0,
        )

    def select_account(self, account_id=None):
        self._query = select(Account, func.sum(self.select_case()).label("balance"))
        if account_id:
            self._query = self._query.filter(Account.id == account_id)

    def join_entries(self):
        self._query = self._query.join(
            TransactionEntry, Account.id == TransactionEntry.account_id
        ).group_by(Account.id)


def create_account(session, account):
    account = Account(name=account.name, type=account.type)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_account_by_id(session, account_id):
    builder = BalanceQueryBuilder()
    builder.select_account(account_id)
    builder.join_entries()

    res = session.execute(builder.query).first()
    return {
        "id": res[0].id,
        "name": res[0].name,
        "type": res[0].type,
        "balance": res[1],
    }


def list_accounts(session):
    builder = BalanceQueryBuilder()
    builder.select_account()
    builder.join_entries()

    res = session.execute(builder.query).all()
    return [
        {
            "id": r[0].id,
            "name": r[0].name,
            "type": r[0].type,
            "balance": r[1],
        }
        for r in res
    ]
