from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, conlist

from db.transactions import MAX_DESC_LEN, TransactionType


class TransactionEntry(BaseModel):
    accountId: UUID
    amount: Decimal = Field(..., gt=0)
    type: TransactionType


class TransactionCreate(BaseModel):
    description: str = Field(..., min_length=20, max_length=MAX_DESC_LEN)
    date: str | None = Field(default=None)
    entries: conlist(TransactionEntry, min_length=2)


class TransactionRead(BaseModel):
    id: UUID
    description: str
    date: str
    entries: list[TransactionEntry]
