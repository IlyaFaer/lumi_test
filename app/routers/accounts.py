from fastapi import APIRouter

from db import SessionDep
from models.accounts import AccountCreate
from services.accounts import create_account, get_account_by_id, list_accounts

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/")
def get_accounts(session: SessionDep):
    return list_accounts(session)


@router.post("/", status_code=201)
def post_account(session: SessionDep, account: AccountCreate):
    return create_account(session, account)


@router.get("/{account_id}")
def get_account(account_id: str, session: SessionDep):
    return get_account_by_id(session, account_id)
