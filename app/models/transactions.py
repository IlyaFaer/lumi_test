from pydantic import BaseModel, Field

from db.transactions import MAX_DESC_LEN


class TransactionEntryCreate(BaseModel):
    accountId: str
    amount: float
    type: str


class TransactionCreate(BaseModel):
    description: str | None = Field(default=None, max_length=MAX_DESC_LEN)
    date: str | None = Field(default=None)
    entries: list[TransactionEntryCreate]
