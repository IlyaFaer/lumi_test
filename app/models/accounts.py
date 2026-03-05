from decimal import Decimal

from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    type: str


class AccountRead(BaseModel):
    id: str
    name: str
    type: str
    balance: Decimal
