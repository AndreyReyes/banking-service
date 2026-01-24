from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.transactions import TransactionRead


class StatementResponse(BaseModel):
    account_id: int
    currency: str
    balance: int
    generated_at: datetime
    transactions: list[TransactionRead]
