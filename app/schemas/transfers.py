from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=10)


class TransferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_account_id: int
    to_account_id: int
    amount: int
    currency: str
    created_at: datetime
