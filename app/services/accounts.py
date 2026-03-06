from typing import Any

from fastapi import HTTPException
import sqlalchemy
from sqlalchemy import case, func, select
from sqlalchemy.sql.expression import Case
from sqlalchemy.sql.selectable import Select
from sqlmodel import Session

from db.accounts import Account, AccountType
from db.transactions import TransactionEntry, TransactionType
from models.accounts import AccountCreate


class BalanceQueryBuilder:
    """
    An utility class to build account balance calculation query.

    Follows the Builder design pattern.
    """

    def __init__(self):
        self._query = None

    @property
    def query(self) -> Select:
        """
        The resulting query to calculate an account and calculate its balance.
        """
        return self._query

    def select_case(self) -> Case[Any]:
        """
        Shape the CASE-WHEN-THEN statement to process
        different variants of credit/debit sum meaning.
        """
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
                asset_or_expense
                & (TransactionEntry.type == TransactionType.Debit),
                TransactionEntry.amount,
            ),
            (
                asset_or_expense
                & (TransactionEntry.type == TransactionType.Credit),
                -TransactionEntry.amount,
            ),
            (
                liability_or_revenue
                & (TransactionEntry.type == TransactionType.Debit),
                -TransactionEntry.amount,
            ),
            (
                liability_or_revenue
                & (TransactionEntry.type == TransactionType.Credit),
                TransactionEntry.amount,
            ),
            else_=0,
        )

    def select_account(self, account_id: str = None):
        """Build the SELECT and WHERE clauses."""
        self._query = select(
            Account.id.label("id"),
            Account.name.label("name"),
            Account.type.label("type"),
            func.sum(self.select_case()).label("balance"),
        )
        if account_id:
            self._query = self._query.filter(Account.id == account_id)

    def join_entries(self, outer: bool = False):
        """Build JOIN and GROUP BY clauses."""
        self._query = self._query.join(
            TransactionEntry,
            Account.id == TransactionEntry.account_id,
            isouter=outer,
        )

        self._query = self._query.group_by(Account.id)


def create_account(session: Session, account: AccountCreate) -> dict:
    """Create a new account in the database."""
    account = Account(name=account.name, type=account.type)
    session.add(account)
    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Account with the name '{account.name}' already exists.",
        )
    session.refresh(account)

    return {
        "id": account.id,
        "name": account.name,
        "type": account.type,
        "balance": 0,
    }


def get_account_by_id(session: Session, account_id: str) -> dict:
    """Read a single account by its id."""
    builder = BalanceQueryBuilder()
    builder.select_account(account_id)
    builder.join_entries()

    res = session.execute(builder.query).mappings().first()
    if res is None:
        raise HTTPException(
            detail="Account with the given id is not found.",
            status_code=404,
        )
    return res


def list_accounts(session: Session) -> list[dict]:
    """List all the accounts."""
    builder = BalanceQueryBuilder()
    builder.select_account()
    builder.join_entries(outer=True)

    return session.execute(builder.query).mappings().all()
