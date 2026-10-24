import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from app.config import Settings, get_settings
from app.data.elexon_client import ElexonClient, ElexonClientError
from app.data.normalize import normalize_actuals, normalize_forecasts


METADATA_NAME = "metadata.json"
ACTUALS_NAME = "actuals.json"
FORECASTS_NAME = "forecasts.json"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, default=str), encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def forecast_publish_window(settings: Settings) -> tuple[datetime, datetime]:
    start = date.fromisoformat(settings.analysis_period_start)
    end = date.fromisoformat(settings.analysis_period_end)
    zone = ZoneInfo(settings.decision_timezone)
    publish_from = datetime.combine(start - timedelta(days=10), datetime.min.time(), tzinfo=zone).astimezone(
        timezone.utc
    )
    publish_to = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=zone).astimezone(
        timezone.utc
    )
    return publish_from, publish_to


def cache_paths(settings: Settings) -> dict[str, Path]:
    return {
        "metadata": settings.cache_dir / METADATA_NAME,
        "actuals": settings.cache_dir / ACTUALS_NAME,
        "forecasts": settings.cache_dir / FORECASTS_NAME,
    }


def cache_is_complete(settings: Settings) -> bool:
    paths = cache_paths(settings)
    return all(path.exists() and path.stat().st_size > 2 for path in paths.values())


def load_cached_records(settings: Settings) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    paths = cache_paths(settings)
    return _read_json(paths["actuals"]), _read_json(paths["forecasts"]), _read_json(paths["metadata"])


def load_demo_records(settings: Settings) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    actuals = _read_json(settings.demo_dir / ACTUALS_NAME)
    forecasts = _read_json(settings.demo_dir / FORECASTS_NAME)
    metadata = {
        "source": "demonstration",
        "labelled_as_demonstration": True,
        "actuals_dataset": "FUELHH (demonstration, not official Elexon observations)",
        "forecasts_dataset": "WINDFOR (demonstration, not official Elexon observations)",
        "last_successful_refresh": None,
        "notes": [
            "Demonstration records are synthetic and must not be treated as Elexon observations.",
            "Refresh from the Elexon Insights API to replace this dataset.",
        ],
    }
    return actuals, forecasts, metadata


def refresh_from_elexon(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    client = ElexonClient(settings)
    start = date.fromisoformat(settings.analysis_period_start)
    end = date.fromisoformat(settings.analysis_period_end)
    publish_from, publish_to = forecast_publish_window(settings)
    actuals = client.fetch_actual_wind(start, end)
    forecasts = client.fetch_wind_forecasts(publish_from, publish_to)
    if not actuals or not forecasts:
        raise ElexonClientError("Elexon returned an empty dataset")
    normalize_actuals(actuals)
    normalize_forecasts(forecasts)
    refreshed_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "source": "elexon",
        "labelled_as_demonstration": False,
        "actuals_dataset": "FUELHH",
        "forecasts_dataset": "WINDFOR",
        "last_successful_refresh": refreshed_at,
        "actual_record_count": len(actuals),
        "forecast_record_count": len(forecasts),
        "notes": [
            "National GB wind generation from Elexon Insights, fuelType=WIND.",
            "Generation values are average MW over the published interval.",
            "No API key is required for the public Insights REST API.",
        ],
    }
    paths = cache_paths(settings)
    _write_json(paths["actuals"], actuals)
    _write_json(paths["forecasts"], forecasts)
    _write_json(paths["metadata"], metadata)
    return metadata


def load_source_records(settings: Settings, allow_demo_fallback: bool = True) -> tuple[list[dict], list[dict], dict]:
    if cache_is_complete(settings):
        return load_cached_records(settings)
    try:
        refresh_from_elexon(settings)
        return load_cached_records(settings)
    except Exception:
        if allow_demo_fallback and (settings.demo_dir / ACTUALS_NAME).exists():
            return load_demo_records(settings)
        raise
