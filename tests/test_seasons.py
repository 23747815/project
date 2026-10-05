"""Checks for calendar mapping and analyses with incomplete weather records."""

from datetime import date, datetime
import unittest

import pandas as pd

from src.seasons import (
    SEASON_ORDER,
    WIND_DIRECTIONS,
    add_seasons_column,
    get_noongar_season,
    longest_dry_spell,
    monthly_statistics,
    seasonal_average,
    seasonal_statistics,
    seasonal_summary,
    wind_direction_frequencies,
    wind_shift_summary,
)


def weather_frame(dates, **measurements):
    """Build a small weather table with optional missing observations."""
    data = {
        "Date": pd.to_datetime(dates),
        "MinTemp": [10.0] * len(dates),
        "MaxTemp": [25.0] * len(dates),
        "Rainfall": [0.0] * len(dates),
        "Sunshine": [8.0] * len(dates),
    }
    data.update(measurements)
    return add_seasons_column(pd.DataFrame(data))


class SeasonMappingTests(unittest.TestCase):
    def test_all_months_and_datetime_types(self):
        expected = [
            "Birak", "Bunuru", "Bunuru", "Djeran", "Djeran", "Makuru",
            "Makuru", "Djilba", "Djilba", "Kambarang", "Kambarang", "Birak",
        ]
        for month, season in enumerate(expected, start=1):
            for value in (date(2024, month, 1), datetime(2024, month, 1),
                          pd.Timestamp(2024, month, 1)):
                with self.subTest(value=value):
                    self.assertEqual(get_noongar_season(value), season)
        self.assertEqual(get_noongar_season(pd.Timestamp("2024-02-29")), "Bunuru")

    def test_add_column_preserves_existing_in_place_behavior(self):
        frame = pd.DataFrame({"Date": pd.to_datetime(["2026-06-01"])})
        result = add_seasons_column(frame)
        self.assertIs(result, frame)
        self.assertEqual(result["Season"].tolist(), ["Makuru"])

    def test_existing_summary_functions_keep_their_columns(self):
        frame = weather_frame(["2026-01-01", "2026-01-02"], MaxTemp=[20.0, 30.0])
        average = seasonal_average(frame, "MaxTemp")
        self.assertEqual(average.columns.tolist(), ["Season", "AverageMaxTemp"])
        self.assertEqual(average.loc[0, "AverageMaxTemp"], 25.0)
        summary = seasonal_summary(frame)
        self.assertEqual(summary.columns.tolist(), [
            "Season", "AverageMinTemp", "AverageMaxTemp", "AverageRainfall", "AverageSunshine",
        ])


class SeasonalStatisticsTests(unittest.TestCase):
    def test_missing_values_use_measurement_specific_denominators(self):
        frame = weather_frame(
            ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
            MinTemp=[9.0, 10.0, None, 11.0],
            MaxTemp=[35.0, None, 34.0, 36.0],
            Rainfall=[0.0, 1.0, None, 3.0],
            Sunshine=[8.0, None, 4.0, None],
            Humidity3pm=[20.0, None, 40.0, None],
        )
        result = seasonal_statistics(frame)
        self.assertEqual(result.index.tolist(), SEASON_ORDER)
        birak = result.loc["Birak"]
        self.assertEqual(birak["Days"], 4)
        for column in ["TemperatureDays", "MinTemperatureDays", "RainfallDays"]:
            self.assertEqual(birak[column], 3)
        self.assertEqual(birak["SunshineDays"], 2)
        self.assertEqual(birak["MeanMaxTemp"], 35)
        self.assertEqual(birak["MedianMaxTemp"], 35)
        self.assertEqual(birak["MaxTempStd"], 1)
        self.assertEqual(birak["TotalRainfall"], 4)
        self.assertAlmostEqual(birak["MeanRainfall"], 4 / 3)
        self.assertEqual(birak["WetDays"], 2)
        self.assertAlmostEqual(birak["WetDayPercent"], 200 / 3)
        self.assertAlmostEqual(birak["HotDayPercent"], 200 / 3)
        self.assertAlmostEqual(birak["CoolNightPercent"], 100 / 3)
        self.assertEqual(birak["MeanSunshine"], 6)
        self.assertEqual(birak["MeanDailyRange"], 25.5)
        self.assertEqual(birak["DailyRangeDays"], 2)
        self.assertEqual(birak["MeanHumidity3pm"], 30)
        self.assertEqual(birak["Humidity3pmDays"], 2)
        self.assertEqual(result.loc["Makuru", "Days"], 0)
        self.assertTrue(pd.isna(result.loc["Makuru", "TotalRainfall"]))

    def test_unknown_rainfall_is_not_reported_as_dry_weather(self):
        frame = weather_frame(
            ["2026-06-01", "2026-06-02"], Rainfall=[float("nan"), float("nan")]
        )
        result = seasonal_statistics(frame).loc["Makuru"]
        self.assertEqual(result["RainfallDays"], 0)
        for column in ["TotalRainfall", "MeanRainfall", "WetDays", "WetDayPercent", "LongestDrySpell"]:
            with self.subTest(column=column):
                self.assertTrue(pd.isna(result[column]))

    def test_no_rows_retains_all_seasons_and_zero_counts(self):
        result = seasonal_statistics(weather_frame([]))
        self.assertEqual(result.index.tolist(), SEASON_ORDER)
        self.assertTrue((result["Days"] == 0).all())
        self.assertTrue(result["MeanMaxTemp"].isna().all())


class DrySpellTests(unittest.TestCase):
    def test_missing_rain_and_missing_dates_break_spells(self):
        frame = weather_frame(
            ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04",
             "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09"],
            Rainfall=[0, 0.2, None, 0, 0, 0, 0, 1],
        )
        self.assertEqual(longest_dry_spell(frame.iloc[::-1]), 3)

    def test_season_changes_break_spells(self):
        frame = weather_frame(pd.date_range("2026-01-30", "2026-02-02"))
        self.assertEqual(longest_dry_spell(frame), 2)

    def test_birak_crosses_new_year_but_separate_occurrences_do_not_join(self):
        frame = weather_frame([
            "2025-12-30", "2025-12-31", "2026-01-01", "2026-01-02",
            "2026-12-30", "2026-12-31", "2027-01-01",
        ])
        self.assertEqual(longest_dry_spell(frame), 4)
        self.assertEqual(seasonal_statistics(frame).loc["Birak", "LongestDrySpell"], 4)

    def test_wet_threshold_and_all_wet_data(self):
        frame = weather_frame(["2026-06-01", "2026-06-02"], Rainfall=[1.0, 2.0])
        self.assertEqual(longest_dry_spell(frame), 0)
        self.assertEqual(longest_dry_spell(frame, threshold=3), 2)


class MonthlyStatisticsTests(unittest.TestCase):
    def test_months_include_missing_month_and_observation_counts(self):
        frame = weather_frame(
            ["2026-01-01", "2026-01-02", "2026-03-01"],
            MaxTemp=[20.0, 30.0, None],
            Rainfall=[None, None, 5.0],
        )
        result = monthly_statistics(frame)
        self.assertEqual(result.index.tolist(), list(pd.date_range("2026-01-01", periods=3, freq="MS")))
        self.assertEqual(result.index.name, "Date")
        self.assertEqual(result.loc["2026-01-01", "MeanMaxTemp"], 25)
        self.assertEqual(result.loc["2026-01-01", "TemperatureDays"], 2)
        self.assertEqual(result.loc["2026-02-01", "Days"], 0)
        self.assertEqual(result.loc["2026-03-01", "Days"], 1)
        self.assertEqual(result.loc["2026-03-01", "TemperatureDays"], 0)
        self.assertTrue(pd.isna(result.loc["2026-01-01", "TotalRainfall"]))
        self.assertTrue(pd.isna(result.loc["2026-02-01", "TotalRainfall"]))
        self.assertEqual(result.loc["2026-03-01", "TotalRainfall"], 5)


class WindDirectionTests(unittest.TestCase):
    def test_valid_directions_only_and_calm_is_normalised(self):
        frame = weather_frame(
            pd.date_range("2026-01-01", periods=6),
            WindDirection9am=[" n ", "N", "sw", "CALM", "unknown", None],
        )
        result = wind_direction_frequencies(frame, "WindDirection9am")
        self.assertEqual(result.index.tolist(), SEASON_ORDER)
        self.assertEqual(result.columns.tolist(), WIND_DIRECTIONS)
        self.assertEqual(result.loc["Birak", "N"], 50)
        self.assertEqual(result.loc["Birak", "SW"], 25)
        self.assertEqual(result.loc["Birak", "Calm"], 25)
        self.assertAlmostEqual(result.loc["Birak"].sum(), 100)
        self.assertTrue(result.loc["Makuru"].isna().all())

    def test_all_missing_or_invalid_directions_remain_unknown(self):
        frame = weather_frame(
            ["2026-06-01", "2026-06-02"], WindDirection9am=[None, "VARIABLE"]
        )
        result = wind_direction_frequencies(frame, "WindDirection9am")
        self.assertEqual(result.shape, (6, 17))
        self.assertTrue(result.isna().all().all())


class WindShiftTests(unittest.TestCase):
    def test_paired_denominator_includes_calm_but_excludes_missing_or_invalid(self):
        frame = weather_frame(
            pd.date_range("2026-01-01", periods=9),
            WindDirection9am=[" e ", "ene", "ese", "CALM", "E", "E", None, "VARIABLE", "E"],
            WindDirection3pm=[" sw ", "ssw", "wsw", "SW", " calm ", None, "SW", "SW", "VARIABLE"],
        )
        result = wind_shift_summary(frame)
        self.assertEqual(result.index.tolist(), SEASON_ORDER)
        self.assertEqual(result.loc["Birak", "PairedWindDays"], 5)
        self.assertEqual(result.loc["Birak", "EastToSWDays"], 3)
        self.assertEqual(result.loc["Birak", "EastToSWPercent"], 60)
        self.assertEqual(result.loc["Makuru", "PairedWindDays"], 0)
        self.assertTrue(pd.isna(result.loc["Makuru", "EastToSWPercent"]))

    def test_all_invalid_pairs_have_unknown_percentages(self):
        frame = weather_frame(
            ["2026-06-01", "2026-06-02"],
            WindDirection9am=[None, "E"],
            WindDirection3pm=["SW", "VARIABLE"],
        )
        result = wind_shift_summary(frame)
        self.assertTrue((result["PairedWindDays"] == 0).all())
        self.assertTrue((result["EastToSWDays"] == 0).all())
        self.assertTrue(result["EastToSWPercent"].isna().all())

    def test_valid_non_matching_pairs_are_zero_percent(self):
        frame = weather_frame(
            ["2026-06-01", "2026-06-02"],
            WindDirection9am=["N", "SW"],
            WindDirection3pm=["SW", "E"],
        )
        result = wind_shift_summary(frame).loc["Makuru"]
        self.assertEqual(result["PairedWindDays"], 2)
        self.assertEqual(result["EastToSWDays"], 0)
        self.assertEqual(result["EastToSWPercent"], 0)


if __name__ == "__main__":
    unittest.main()
