from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


CardType = Literal["virtual", "physical"]
CardStatus = Literal["active", "blocked"]


class CardCreate(BaseModel):
    account_id: int
    type: CardType


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    type: CardType
    last4: str
    status: CardStatus
    created_at: datetime
