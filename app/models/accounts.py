from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    type: str
