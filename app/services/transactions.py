from db.transactions import Transaction, TransactionEntry


def create_transaction(session, transaction_raw):
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
    return session.query(Transaction).filter(Transaction.id == transaction_id).first()


def list_transactions_by_account_id(session, account_id):
    return (
        session.query(TransactionEntry)
        .filter((TransactionEntry.account_id == account_id))
        .all()
    )
