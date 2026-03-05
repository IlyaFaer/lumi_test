from fastapi import APIRouter

from db import SessionDep
from models.accounts import AccountCreate, AccountRead
from models.transactions import TransactionRead
from services.accounts import create_account, get_account_by_id, list_accounts
from services.transactions import list_transactions_by_account_id

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/")
def get_accounts(session: SessionDep) -> list[AccountRead]:
    return list_accounts(session)


@router.post("/", status_code=201)
def post_account(session: SessionDep, account: AccountCreate) -> AccountRead:
    return create_account(session, account)


@router.get("/{account_id}")
def get_account(account_id: str, session: SessionDep) -> AccountRead:
    return get_account_by_id(session, account_id)


@router.get("/{account_id}/transactions")
def get_account_transactions(
    account_id: str, session: SessionDep
) -> list[TransactionRead]:
    return list_transactions_by_account_id(session, account_id)
