import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def build_demo() -> tuple[list[dict], list[dict]]:
    actuals: list[dict] = []
    forecasts: list[dict] = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for index in range(31 * 48):
        start_time = start + timedelta(minutes=30 * index)
        generation = 8500 + 3500 * math.sin(index / 10.0) + 120 * (index % 11)
        actuals.append(
            {
                "dataset": "DEMO-FUELHH",
                "publishTime": (start_time + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "settlementDate": start_time.date().isoformat(),
                "settlementPeriod": (index % 48) + 1,
                "fuelType": "WIND",
                "generation": round(generation, 1),
            }
        )
    first_publish_day = datetime(2025, 12, 31, 7, 30, tzinfo=timezone.utc)
    for day in range(32):
        publish_time = first_publish_day + timedelta(days=day)
        delivery = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=day)
        for hour in range(24):
            start_time = delivery + timedelta(hours=hour)
            if start_time.year != 2026 or start_time.month != 1:
                continue
            index = day * 24 + hour
            generation = 8700 + 3200 * math.sin((index + 3) / 10.0) + 80 * (index % 9)
            forecasts.append(
                {
                    "dataset": "DEMO-WINDFOR",
                    "publishTime": publish_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "generation": round(generation, 1),
                }
            )
            late = publish_time.replace(hour=9, minute=30)
            forecasts.append(
                {
                    "dataset": "DEMO-WINDFOR",
                    "publishTime": late.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "generation": round(generation + 2500, 1),
                }
            )
    return actuals, forecasts


def write_demo(directory: Path) -> None:
    actuals, forecasts = build_demo()
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "actuals.json").write_text(json.dumps(actuals), encoding="utf-8")
    (directory / "forecasts.json").write_text(json.dumps(forecasts), encoding="utf-8")


if __name__ == "__main__":
    write_demo(Path(__file__).resolve().parent.parent.parent / "data" / "demo")
