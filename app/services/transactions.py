from collections import Counter

from fastapi import HTTPException

from db.transactions import Transaction, TransactionEntry
from sqlmodel import select


def _validate_entries(entries):
    c = Counter()
    for e in entries:
        c[e.type] += e.amount

    if c["DEBIT"] != c["CREDIT"]:
        raise HTTPException(
            status_code=400, detail="Total DEBIT and CREDIT amounts must be equal!"
        )


def create_transaction(session, transaction_raw):
    _validate_entries(transaction_raw.entries)

    transaction = Transaction(
        description=transaction_raw.description, timestamp=transaction_raw.date
    )
    session.add(transaction)
    for entry in transaction_raw.entries:
        transaction_entry = TransactionEntry(
            transaction_id=transaction.id,
            account_id=entry.accountId,
            type=entry.type,
            amount=entry.amount,
        )
        session.add(transaction_entry)

    session.commit()
    session.refresh(transaction)
    return transaction


def get_transaction_by_id(session, transaction_id):
    transaction = (
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
    entries = (
        session.execute(
            select(
                TransactionEntry.id.label("id"),
                TransactionEntry.account_id.label("account_id"),
                TransactionEntry.type.label("type"),
                TransactionEntry.amount.label("amount"),
            ).filter(TransactionEntry.transaction_id == transaction_id)
        )
        .mappings()
        .all()
    )
    return {
        "id": transaction["id"],
        "date": transaction["timestamp"].isoformat(),
        "description": transaction["description"],
        "entries": entries,
    }


def list_transactions_by_account_id(session, account_id):
    res = (
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
            .join(Transaction, TransactionEntry.transaction_id == Transaction.id)
        )
        .mappings()
        .all()
    )

    transactions = {}
    for entry in res:
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
                "account_id": entry["account_id"],
                "type": entry["type"],
                "transaction_id": entry["transaction_id"],
                "amount": entry["amount"],
            }
        )

    res = [transaction for transaction in transactions.values()]
    return res
