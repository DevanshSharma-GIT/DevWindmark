from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.analysis.selection import decision_cutoff_for_interval
from app.config import Settings


def test_cutoff_respects_british_summer_time():
    settings = Settings(decision_timezone="Europe/London", decision_cutoff_time="09:20", decision_offset_days=1)
    start = datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc)
    cutoff = decision_cutoff_for_interval(start, settings)
    local = datetime(2026, 3, 29, 9, 20, tzinfo=ZoneInfo("Europe/London"))
    assert cutoff == local.astimezone(timezone.utc)
    assert cutoff.hour == 8
    assert cutoff.minute == 20
