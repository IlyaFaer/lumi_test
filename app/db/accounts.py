import uuid
from enum import Enum
from sqlmodel import SQLModel, Field


class AccountType(str, Enum):
    Cash = "cash"
    Revenue = "revenue"
    Expenses = "expenses"
    Liability = "liability"


class Account(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(..., unique=True)
    type: AccountType = Field(...)
