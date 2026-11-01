from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from rasoi.config import Campaign


@dataclass
class DataBundle:
    customers: pd.DataFrame
    orders: pd.DataFrame
    trial: pd.DataFrame
    campaign: Campaign


def _read_parquet(root: Path, name: str) -> pd.DataFrame:
    frame = pd.read_parquet(root / name)
    for column in ("signup_date", "order_ts", "offer_date"):
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column])
    return frame


def load_bundle(data_dir: str | Path) -> DataBundle:
    root = Path(data_dir)
    return DataBundle(
        customers=_read_parquet(root, "customers.parquet"),
        orders=_read_parquet(root, "orders_180d.parquet"),
        trial=_read_parquet(root, "trial.parquet"),
        campaign=Campaign.load(root / "campaign.json"),
    )
