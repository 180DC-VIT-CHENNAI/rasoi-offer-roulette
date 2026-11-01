from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    snapshot_date: date
    trial_offer_date: date
    campaign_date: date
    campaign_window_days: int
    customers: int
    profit_per_order_inr: float
    discount_budget_inr: float

    @classmethod
    def load(cls, path: str | Path) -> Campaign:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            campaign_id=payload["campaign_id"],
            snapshot_date=date.fromisoformat(payload["snapshot_date"]),
            trial_offer_date=date.fromisoformat(payload["trial_offer_date"]),
            campaign_date=date.fromisoformat(payload["campaign_date"]),
            campaign_window_days=int(payload["campaign_window_days"]),
            customers=int(payload["customers"]),
            profit_per_order_inr=float(payload["economics"]["profit_per_order_before_discount_inr"]),
            discount_budget_inr=float(payload["economics"]["discount_budget_inr"]),
        )
