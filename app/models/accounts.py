from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from db import AccountType


class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: AccountType


class AccountRead(BaseModel):
    id: UUID
    name: str
    type: AccountType
    balance: Decimal
