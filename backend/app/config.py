from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DevWindmark"
    analysis_period_start: str = "2026-01-01"
    analysis_period_end: str = "2026-01-31"
    decision_timezone: str = "Europe/London"
    decision_cutoff_time: str = "09:20"
    decision_offset_days: int = 1
    generation_unit: str = "MW"
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    elexon_timeout_seconds: float = 60.0
    elexon_max_retries: int = 4
    cache_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "cache")
    demo_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "demo")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://frontend:80"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
