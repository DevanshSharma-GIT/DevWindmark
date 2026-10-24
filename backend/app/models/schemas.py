from typing import Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    application: str
    analysis_period_start: str
    analysis_period_end: str


class DataProvenance(BaseModel):
    source: Literal["elexon", "demonstration"]
    labelled_as_demonstration: bool
    actuals_dataset: str
    forecasts_dataset: str
    generation_unit: str
    last_successful_refresh: Optional[str] = None
    notes: list[str] = Field(default_factory=list)


class CoverageStats(BaseModel):
    expected_intervals: int
    matched_intervals: int
    missing_actuals: int
    missing_forecasts: int
    coverage_percent: float


class SummaryMetrics(BaseModel):
    mae_mw: Optional[float] = None
    rmse_mw: Optional[float] = None
    mean_forecast_error_mw: Optional[float] = None
    mean_actual_mw: Optional[float] = None
    mean_forecast_mw: Optional[float] = None
    matched_intervals: int
    coverage: CoverageStats


class IntervalRecord(BaseModel):
    start_time: str
    delivery_date: str
    settlement_period: Optional[int] = None
    actual_generation_mw: Optional[float] = None
    forecast_generation_mw: Optional[float] = None
    forecast_publish_time: Optional[str] = None
    decision_cutoff: str
    forecast_error_mw: Optional[float] = None
    absolute_forecast_error_mw: Optional[float] = None
    missing_actual: bool
    missing_forecast: bool


class SummaryResponse(BaseModel):
    application: str
    analysis_period_start: str
    analysis_period_end: str
    decision_cutoff_policy: str
    generation_unit: str
    provenance: DataProvenance
    metrics: SummaryMetrics
    selected_interval: Optional[IntervalRecord] = None


class ForecastsResponse(BaseModel):
    generation_unit: str
    decision_cutoff_policy: str
    provenance: DataProvenance
    coverage: CoverageStats
    intervals: list[IntervalRecord]


class HistogramBin(BaseModel):
    bin_start_mw: float
    bin_end_mw: float
    count: int


class DailyAccuracy(BaseModel):
    delivery_date: str
    matched_intervals: int
    mae_mw: Optional[float] = None
    rmse_mw: Optional[float] = None
    mean_forecast_error_mw: Optional[float] = None
    mean_actual_mw: Optional[float] = None
    mean_forecast_mw: Optional[float] = None


class TimeOfDayAccuracy(BaseModel):
    hour_ending_utc: int
    matched_intervals: int
    mae_mw: Optional[float] = None
    rmse_mw: Optional[float] = None
    mean_forecast_error_mw: Optional[float] = None


class AccuracyResponse(BaseModel):
    generation_unit: str
    error_convention: str
    provenance: DataProvenance
    metrics: SummaryMetrics
    error_histogram: list[HistogramBin]
    daily: list[DailyAccuracy]
    time_of_day: list[TimeOfDayAccuracy]
    scatter: list[IntervalRecord]
    error_series: list[IntervalRecord]


class InsightsResponse(BaseModel):
    provenance: DataProvenance
    overforecast_share_percent: Optional[float] = None
    underforecast_share_percent: Optional[float] = None
    largest_overforecast_mw: Optional[float] = None
    largest_underforecast_mw: Optional[float] = None
    highest_mae_dates: list[DailyAccuracy]
    lowest_mae_dates: list[DailyAccuracy]
    observations: list[str]
    limitations: list[str]


class MethodologyResponse(BaseModel):
    application: str
    data_sources: list[str]
    forecast_selection_policy: list[str]
    decision_cutoff: dict
    timestamp_handling: list[str]
    metric_definitions: dict
    missing_data: list[str]
    limitations: list[str]
    reproducibility: list[str]
    provenance: DataProvenance
