from enum import Enum
from sqlmodel import SQLModel, Field
import uuid


class AccountType(str, Enum):
    Asset = "ASSET"
    Revenue = "REVENUE"
    Expenses = "EXPENSES"
    Liability = "LIABILITY"


class Account(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(..., unique=True)
    type: AccountType = Field(...)
