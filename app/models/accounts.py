from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    type: str


class AccountRead(BaseModel):
    id: UUID
    name: str
    type: str
    balance: Decimal
