from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TransactionType = Literal["deposit", "withdrawal", "transfer_in", "transfer_out"]


class TransactionCreate(BaseModel):
    account_id: int
    type: TransactionType
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=10)


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    type: TransactionType
    amount: int
    currency: str
    created_at: datetime
