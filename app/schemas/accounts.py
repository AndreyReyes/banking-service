from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AccountType = Literal["checking", "savings"]
AccountStatus = Literal["active", "frozen", "closed"]


class AccountCreate(BaseModel):
    type: AccountType
    currency: str = Field(min_length=3, max_length=10)


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    holder_id: int
    type: AccountType
    currency: str
    balance: int
    status: AccountStatus
    created_at: datetime
