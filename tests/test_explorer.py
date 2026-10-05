"""Pytest checks for season classification, analysis and the saved GUI dataset.

Run pytest from the project root. The saved dataset is only read, never rebuilt.
"""

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from src.seasons import (
    add_seasons_column,
    get_noongar_season,
    seasonal_average,
    seasonal_statistics,
)
from src.seasons_analysis import data_quality


EXPECTED_SEASONS = {"Birak", "Bunuru", "Djeran", "Makuru", "Djilba", "Kambarang"}
DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "outputs" / "seasons" / "daily_weather_with_seasons.csv"
)


# Each parameter row is collected as a separate test by pytest.
@pytest.mark.parametrize("month, expected", [
    (1, "Birak"), (2, "Bunuru"), (3, "Bunuru"), (4, "Djeran"),
    (5, "Djeran"), (6, "Makuru"), (7, "Makuru"), (8, "Djilba"),
    (9, "Djilba"), (10, "Kambarang"), (11, "Kambarang"), (12, "Birak"),
])
def test_each_month_has_the_expected_season(month, expected):
    assert get_noongar_season(date(2026, month, 15)) == expected


@pytest.mark.parametrize("last_day, first_day, before, after", [
    ("2026-01-31", "2026-02-01", "Birak", "Bunuru"),
    ("2026-03-31", "2026-04-01", "Bunuru", "Djeran"),
    ("2026-05-31", "2026-06-01", "Djeran", "Makuru"),
    ("2026-07-31", "2026-08-01", "Makuru", "Djilba"),
    ("2026-09-30", "2026-10-01", "Djilba", "Kambarang"),
    ("2026-11-30", "2026-12-01", "Kambarang", "Birak"),
])
def test_season_changes_at_month_boundary(last_day, first_day, before, after):
    assert get_noongar_season(date.fromisoformat(last_day)) == before
    assert get_noongar_season(date.fromisoformat(first_day)) == after


def test_leap_day_is_bunuru():
    assert get_noongar_season(date(2024, 2, 29)) == "Bunuru"


@pytest.mark.parametrize("invalid_date", [None, "2026-01-01"])
def test_season_lookup_requires_a_date_object(invalid_date):
    # The existing function expects .month; it does not parse strings or None.
    with pytest.raises(AttributeError):
        get_noongar_season(invalid_date)


def test_add_seasons_column_preserves_rows_and_measurements():
    frame = pd.DataFrame({
        "Date": pd.to_datetime(["2026-06-01", "2026-01-31", "2026-02-01"]),
        "MaxTemp": [18.0, 32.0, 35.0],
    }, index=[4, 2, 9])
    original = frame.copy()
    result = add_seasons_column(frame)
    assert result["Season"].tolist() == ["Makuru", "Birak", "Bunuru"]
    pd.testing.assert_frame_equal(result[original.columns], original)


def test_add_seasons_column_accepts_an_empty_dataframe():
    frame = pd.DataFrame({"Date": pd.Series(dtype="datetime64[ns]")})
    result = add_seasons_column(frame)
    assert result.empty
    assert result.columns.tolist() == ["Date", "Season"]


def test_add_seasons_column_requires_date_column():
    with pytest.raises(KeyError, match="Date"):
        add_seasons_column(pd.DataFrame({"MaxTemp": [25.0]}))


@pytest.fixture
def sample_weather():
    """Small known inputs make expected averages and totals easy to check."""
    return add_seasons_column(pd.DataFrame({
        "Date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-06-01"]),
        "MinTemp": [10.0, 14.0, 6.0],
        "MaxTemp": [30.0, 34.0, 18.0],
        "Rainfall": [0.0, 2.0, 10.0],
        "Sunshine": [8.0, 10.0, 4.0],
    }))


def test_seasonal_average_keeps_seasons_separate(sample_weather):
    result = seasonal_average(sample_weather, "MaxTemp").set_index("Season")
    assert result.loc["Birak", "AverageMaxTemp"] == pytest.approx(32.0)
    assert result.loc["Makuru", "AverageMaxTemp"] == pytest.approx(18.0)


def test_seasonal_statistics_known_counts_means_and_rainfall(sample_weather):
    result = seasonal_statistics(sample_weather).loc["Birak"]
    assert result["Days"] == 2
    assert result["MeanMinTemp"] == pytest.approx(12.0)
    assert result["MeanMaxTemp"] == pytest.approx(32.0)
    assert result["TotalRainfall"] == pytest.approx(2.0)
    assert result["MeanSunshine"] == pytest.approx(9.0)


def test_missing_rainfall_is_not_treated_as_zero(sample_weather):
    sample_weather.loc[sample_weather["Season"] == "Birak", "Rainfall"] = float("nan")
    result = seasonal_statistics(sample_weather).loc["Birak"]
    assert result["Days"] == 2
    assert result["RainfallDays"] == 0
    assert pd.isna(result["TotalRainfall"])


def test_analysis_data_quality_counts_missing_values(sample_weather):
    sample_weather.loc[0, "Sunshine"] = float("nan")
    result = data_quality(sample_weather)
    assert result.loc["Sunshine", "ObservedDays"] == 2
    assert result.loc["Sunshine", "MissingDays"] == 1
    assert result.loc["Sunshine", "CoveragePercent"] == pytest.approx(200 / 3)
    assert result.loc["Rainfall", "CoveragePercent"] == pytest.approx(100.0)
    assert "Date" not in result.index
    assert "Season" not in result.index


@pytest.fixture(scope="module")
def processed_weather():
    """Read the existing exported dataset once without regenerating any files."""
    return pd.read_csv(DATA_PATH)


def test_processed_dataset_has_required_gui_columns(processed_weather):
    required = {"Date", "Season", "MinTemp", "MaxTemp", "Rainfall", "Sunshine"}
    assert required.issubset(processed_weather.columns)


def test_processed_dataset_has_at_least_200_records(processed_weather):
    assert len(processed_weather) >= 200


def test_processed_dataset_has_all_six_seasons(processed_weather):
    assert processed_weather["Season"].notna().all()
    assert set(processed_weather["Season"]) == EXPECTED_SEASONS


def test_processed_dataset_has_valid_unique_daily_dates(processed_weather):
    dates = pd.to_datetime(processed_weather["Date"], errors="raise")
    assert dates.notna().all()
    assert not dates.dt.normalize().duplicated().any()


def test_saved_seasons_match_the_existing_classifier(processed_weather):
    dates = pd.to_datetime(processed_weather["Date"], errors="raise")
    expected = dates.apply(get_noongar_season)
    assert processed_weather["Season"].tolist() == expected.tolist()
