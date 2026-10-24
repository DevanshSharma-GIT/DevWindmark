from datetime import date, datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

from app.config import Settings


class ElexonClientError(RuntimeError):
    pass


class ElexonClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _get_json(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        url = f"{self.settings.elexon_base_url}{path}"
        query = urlencode(params, doseq=True)
        last_error: Exception | None = None
        for attempt in range(self.settings.elexon_max_retries):
            try:
                with httpx.Client(timeout=self.settings.elexon_timeout_seconds) as client:
                    response = client.get(f"{url}?{query}")
                if response.status_code == 429:
                    raise ElexonClientError("Elexon rate limit (HTTP 429)")
                if response.status_code >= 400:
                    raise ElexonClientError(
                        f"Elexon request failed ({response.status_code}): {response.text[:400]}"
                    )
                payload = response.json()
                if isinstance(payload, dict) and "data" in payload:
                    rows = payload["data"]
                else:
                    rows = payload
                if not isinstance(rows, list):
                    raise ElexonClientError("Unexpected Elexon payload shape")
                return rows
            except (httpx.HTTPError, ElexonClientError, ValueError) as exc:
                last_error = exc
                if attempt == self.settings.elexon_max_retries - 1:
                    break
        raise ElexonClientError(str(last_error)) from last_error

    def fetch_actual_wind(self, start: date, end: date) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        cursor = start
        while cursor <= end:
            chunk_end = min(cursor + timedelta(days=6), end)
            rows.extend(
                self._get_json(
                    "/datasets/FUELHH/stream",
                    {
                        "fuelType": "WIND",
                        "settlementDateFrom": cursor.isoformat(),
                        "settlementDateTo": chunk_end.isoformat(),
                    },
                )
            )
            cursor = chunk_end + timedelta(days=1)
        return rows

    def fetch_wind_forecasts(self, publish_from: datetime, publish_to: datetime) -> list[dict[str, Any]]:
        if publish_from.tzinfo is None:
            publish_from = publish_from.replace(tzinfo=timezone.utc)
        if publish_to.tzinfo is None:
            publish_to = publish_to.replace(tzinfo=timezone.utc)
        rows: list[dict[str, Any]] = []
        cursor = publish_from
        while cursor < publish_to:
            chunk_end = min(cursor + timedelta(days=2), publish_to)
            rows.extend(
                self._get_json(
                    "/datasets/WINDFOR/stream",
                    {
                        "publishDateTimeFrom": cursor.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "publishDateTimeTo": chunk_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    },
                )
            )
            cursor = chunk_end
        return rows
