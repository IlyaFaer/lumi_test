"""The basic database functions and dependencies."""

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated

from .accounts import Account, AccountType  # noqa: F401
from .transactions import (  # noqa: F401
    Transaction,
    TransactionEntry,
    TransactionType,
)


db_url = "postgresql+psycopg://postgres:postgres@db:5432/luminary"
engine = create_engine(db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    """Database sessions generator."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
