from collections import Counter
import re

import sqlalchemy
from fastapi import HTTPException
from sqlmodel import Session, select

from db.transactions import Transaction, TransactionEntry
from models.transactions import TransactionCreate
from services.accounts import AccountNotFoundException


def _validate_entries(entries: list[TransactionCreate]):
    """Check that debit sum is equal to credit sum for this transaction."""
    c = Counter()
    for e in entries:
        c[e.type] += e.amount

    if "DEBIT" not in c or "CREDIT" not in c:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction must have at least one"
                " DEBIT and one CREDIT entry!"
            ),
        )

    if c["DEBIT"] != c["CREDIT"]:
        raise HTTPException(
            status_code=400,
            detail="Total DEBIT and CREDIT amounts must be equal!",
        )


def create_transaction(
    session: Session, transaction_raw: TransactionCreate
) -> dict:
    """Create a new transaction with the given entries."""
    _validate_entries(transaction_raw.entries)

    txn = Transaction(
        description=transaction_raw.description, timestamp=transaction_raw.date
    )
    session.add(txn)

    for entry in transaction_raw.entries:
        transaction_entry = TransactionEntry(
            transaction_id=txn.id,
            account_id=entry.accountId,
            type=entry.type,
            amount=entry.amount,
        )
        session.add(transaction_entry)

    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        session.rollback()

        match = re.search(r"Key \(account_id\)=\(([^)]+)\)", str(exc.orig))
        if match:
            raise AccountNotFoundException(account_id=match.group(1))
    return get_transaction_by_id(session, txn.id)


def get_transaction_by_id(session: Session, transaction_id: str) -> dict:
    """Return a transaction and all of its entries by the given id."""
    txn = (
        session.execute(
            select(
                Transaction.id.label("id"),
                Transaction.timestamp.label("timestamp"),
                Transaction.description.label("description"),
            ).filter(Transaction.id == transaction_id)
        )
        .mappings()
        .first()
    )
    if txn is None:
        raise HTTPException(
            status_code=404, detail="Transaction with the given id not found!"
        )
    entries = (
        session.execute(
            select(
                TransactionEntry.id.label("id"),
                TransactionEntry.account_id.label("accountId"),
                TransactionEntry.type.label("type"),
                TransactionEntry.amount.label("amount"),
            ).filter(TransactionEntry.transaction_id == transaction_id)
        )
        .mappings()
        .all()
    )
    return {
        "id": txn["id"],
        "date": txn["timestamp"].isoformat(),
        "description": txn["description"],
        "entries": entries,
    }


def list_transactions_by_account_id(
    session: Session, account_id: str
) -> list[dict]:
    """Return entries and parent transactions impacted the given account."""
    entries = (
        session.execute(
            select(
                TransactionEntry.id.label("id"),
                TransactionEntry.account_id.label("account_id"),
                TransactionEntry.type.label("type"),
                TransactionEntry.amount.label("amount"),
                Transaction.id.label("transaction_id"),
                Transaction.timestamp.label("date"),
                Transaction.description.label("description"),
            )
            .filter(TransactionEntry.account_id == account_id)
            .join(
                Transaction, TransactionEntry.transaction_id == Transaction.id
            )
        )
        .mappings()
        .all()
    )

    transactions = {}
    for entry in entries:
        tid = entry["transaction_id"]
        if tid not in transactions:
            transactions[tid] = {
                "id": tid,
                "date": entry["date"].isoformat(),
                "description": entry["description"],
                "entries": [],
            }

        transactions[tid]["entries"].append(
            {
                "id": entry["id"],
                "accountId": entry["account_id"],
                "type": entry["type"],
                "transaction_id": entry["transaction_id"],
                "amount": entry["amount"],
            }
        )
    return [transaction for transaction in transactions.values()]
