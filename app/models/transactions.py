from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, conlist

from db.transactions import MAX_DESC_LEN


class TransactionEntryCreate(BaseModel):
    accountId: UUID
    amount: Decimal = Field(..., gt=0)
    type: str


class TransactionCreate(BaseModel):
    description: str = Field(..., min_length=30, max_length=MAX_DESC_LEN)
    date: str | None = Field(default=None)
    entries: conlist(TransactionEntryCreate, min_length=2)


class TransactionEntryRead(BaseModel):
    account_id: UUID
    amount: Decimal
    type: str


class TransactionRead(BaseModel):
    id: UUID
    description: str | None
    date: str
    entries: list[TransactionEntryRead]
