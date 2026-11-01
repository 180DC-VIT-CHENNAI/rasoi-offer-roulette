from __future__ import annotations

from pydantic import BaseModel


class OfferResponse(BaseModel):
    customer_id: str
    offer: str
    expected_discount_inr: float
    expected_incremental_profit_inr: float
    reason: str
