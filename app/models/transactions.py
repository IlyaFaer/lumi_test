from uuid import UUID
from pydantic import BaseModel, Field

from db.transactions import MAX_DESC_LEN


class TransactionEntryCreate(BaseModel):
    accountId: UUID
    amount: float
    type: str


class TransactionCreate(BaseModel):
    description: str | None = Field(default=None, max_length=MAX_DESC_LEN)
    date: str | None = Field(default=None)
    entries: list[TransactionEntryCreate]


class TransactionEntryRead(BaseModel):
    account_id: UUID
    amount: float
    type: str


class TransactionRead(BaseModel):
    id: UUID
    description: str | None
    date: str
    entries: list[TransactionEntryRead]
