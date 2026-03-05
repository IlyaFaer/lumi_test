from db.accounts import Account


def create_account(session, account):
    account = Account(name=account.name, type=account.type)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_account_by_id(session, account_id):
    return session.query(Account).filter(Account.id == account_id).first()


def list_accounts(session):
    return session.query(Account).all()
