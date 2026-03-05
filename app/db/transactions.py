from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field
import uuid

MAX_DESC_LEN = 150


class TransactionType(str, Enum):
    Debit = "DEBIT"
    Credit = "CREDIT"


class Transaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(nullable=True, max_length=MAX_DESC_LEN)


class TransactionEntry(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transaction_id: uuid.UUID = Field(foreign_key="transaction.id")
    account_id: uuid.UUID = Field(foreign_key="account.id")
    type: TransactionType = Field(...)
    amount: Decimal = Field(..., gt=0)
