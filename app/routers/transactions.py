from fastapi import APIRouter

from db import SessionDep
from models.transactions import TransactionCreate, TransactionRead
from services.transactions import create_transaction, retrieve_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: str, session: SessionDep
) -> TransactionRead:
    return retrieve_transaction(session, transaction_id)


@router.post("/", status_code=201)
def post_transaction(
    transaction: TransactionCreate, session: SessionDep
) -> TransactionRead:
    return create_transaction(session, transaction)
