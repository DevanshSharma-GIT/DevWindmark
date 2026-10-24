from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd


def parse_utc(value: Any) -> Optional[datetime]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    parsed = pd.to_datetime(text, utc=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime()


def parse_generation(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number):
        return None
    return number


def normalize_actuals(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for record in records:
        if str(record.get("fuelType", "")).upper() != "WIND":
            continue
        start_time = parse_utc(record.get("startTime"))
        generation = parse_generation(record.get("generation"))
        if start_time is None or generation is None:
            continue
        rows.append(
            {
                "start_time": start_time,
                "publish_time": parse_utc(record.get("publishTime")),
                "settlement_date": str(record.get("settlementDate") or "")[:10] or None,
                "settlement_period": record.get("settlementPeriod"),
                "actual_generation_mw": generation,
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame = frame.sort_values(["start_time", "publish_time"], na_position="first")
    frame = frame.drop_duplicates(subset=["start_time"], keep="last")
    return frame.reset_index(drop=True)


def normalize_forecasts(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for record in records:
        start_time = parse_utc(record.get("startTime"))
        publish_time = parse_utc(record.get("publishTime"))
        generation = parse_generation(record.get("generation"))
        if start_time is None or publish_time is None or generation is None:
            continue
        rows.append(
            {
                "start_time": start_time,
                "publish_time": publish_time,
                "forecast_generation_mw": generation,
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame = frame.sort_values(["start_time", "publish_time", "forecast_generation_mw"])
    frame = frame.drop_duplicates(subset=["start_time", "publish_time"], keep="last")
    return frame.reset_index(drop=True)
