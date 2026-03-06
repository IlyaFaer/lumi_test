from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str


class AccountRead(BaseModel):
    id: UUID
    name: str
    type: str
    balance: Decimal
