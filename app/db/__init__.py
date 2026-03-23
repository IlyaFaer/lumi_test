"""The basic database functions and dependencies."""

import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from .accounts import Account, AccountType  # noqa: F401
from .transactions import (  # noqa: F401
    Transaction,
    TransactionEntry,
    TransactionType,
)


db_url = os.environ.get("DB_URL", "sqlite:///./luminary.db")
engine = create_engine(db_url)


def get_session():
    """Database sessions generator."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
