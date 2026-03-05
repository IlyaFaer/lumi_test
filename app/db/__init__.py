from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from .accounts import Account, AccountType
from .transactions import Transaction, TransactionEntry, TransactionType


db_url = "postgresql+psycopg://postgres:postgres@db:5432/luminary"
engine = create_engine(db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
