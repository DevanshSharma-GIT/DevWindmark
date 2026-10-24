from app.analysis.service import load_analysis_bundle, refresh_and_clear


def refresh() -> None:
    metadata = refresh_and_clear()
    print(f"source={metadata['source']}")
    print(f"actual_records={metadata.get('actual_record_count')}")
    print(f"forecast_records={metadata.get('forecast_record_count')}")
    print(f"refreshed_at={metadata.get('last_successful_refresh')}")


def status() -> None:
    settings, intervals, metadata = load_analysis_bundle()
    print(f"application={settings.app_name}")
    print(f"source={metadata.get('source')}")
    print(f"demonstration={metadata.get('labelled_as_demonstration')}")
    print(f"intervals={len(intervals)}")
    print(f"matched={int((~intervals['missing_actual'] & ~intervals['missing_forecast']).sum())}")


if __name__ == "__main__":
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "refresh":
        refresh()
    elif command == "status":
        status()
    else:
        raise SystemExit("Usage: python -m app.cli [refresh|status]")
