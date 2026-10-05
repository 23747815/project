"""Synthetic BOM downloads test preparation without changing the project data."""

import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from data.combine_data_extended import combine_weather_data


class CombineWeatherDataTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.raw_directory = self.directory / "raw"
        self.raw_directory.mkdir()
        self.output_file = self.directory / "clean" / "weather.csv"

    def write_month(self, name, rows, extra_headers=(), metadata_lines=2,
                    encoding="utf-8", degree_symbol="\u00b0"):
        headers = [
            "", "Date", f"Minimum temperature ({degree_symbol}C)",
            f"Maximum temperature ({degree_symbol}C)", "Rainfall (mm)",
            "Sunshine (hours)", *extra_headers,
        ]
        with (self.raw_directory / name).open("w", encoding=encoding, newline="") as output:
            writer = csv.writer(output)
            for number in range(metadata_lines):
                writer.writerow([f"Metadata line {number}"])
            writer.writerow([])
            writer.writerow(headers)
            for row in rows:
                writer.writerow(["", *row])

    def combine(self):
        return combine_weather_data(self.raw_directory, self.output_file)

    def test_metadata_length_encoding_and_date_order(self):
        self.write_month("later.csv", [["2026-02-1", 13, 30, 0, 11]],
                         metadata_lines=9, encoding="cp1252")
        self.write_month("earlier.csv", [["2026-01-2", 12, 29, 1.2, 10]],
                         metadata_lines=0, degree_symbol="\ufffd")
        result = self.combine()
        self.assertEqual(result["Date"].tolist(), list(pd.to_datetime(["2026-01-02", "2026-02-01"])))
        self.assertEqual(result["SourceFile"].tolist(), ["earlier.csv", "later.csv"])
        self.assertEqual(result["MaxTemp"].tolist(), [29, 30])
        self.assertTrue(result["Evaporation"].isna().all())
        self.assertTrue(result["WindDirection3pm"].isna().all())
        self.assertEqual(len(pd.read_csv(self.output_file)), 2)

    def test_missing_values_are_retained_and_calm_is_distinct_from_missing(self):
        self.write_month("wind.csv", [
            ["2026-01-1", 12, 30, "", 10, " ", "Calm", " sw ", 19, " ", 45],
            ["2026-01-2", " ", 31, 0, "invalid", " ", " ", "", "", 5.2, "invalid"],
            ["invalid-date", 12, 30, 0, 10, "E", 9, "SW", 19, 5.2, 45],
        ], extra_headers=[
            "9am wind direction", "9am wind speed (km/h)",
            "3pm wind direction", "3pm wind speed (km/h)",
            "Evaporation (mm)", "3pm relative humidity (%)",
        ])
        result = self.combine()
        self.assertEqual(len(result), 2)
        self.assertTrue(pd.isna(result.loc[0, "Rainfall"]))
        self.assertEqual(result.loc[0, "WindSpeed9am"], 0)
        self.assertEqual(result.loc[0, "WindDirection9am"], "CALM")
        self.assertEqual(result.loc[0, "WindDirection3pm"], "SW")
        self.assertEqual(result.loc[0, "WindSpeed3pm"], 19)
        self.assertTrue(pd.isna(result.loc[1, "WindSpeed9am"]))
        self.assertTrue(pd.isna(result.loc[1, "WindDirection9am"]))
        self.assertTrue(pd.isna(result.loc[1, "Humidity3pm"]))
        self.assertTrue(pd.isna(result.loc[1, "Sunshine"]))

    def test_optional_measurements_map_to_the_correct_time_and_units(self):
        self.write_month("extended.csv", [[
            "2026-01-1", 10, 25, 0.2, 9, 3.2, "NW", 54,
            17, 76, 7, 1023.1, 24, 48, 2, 1021.4,
        ]], extra_headers=[
            "Evaporation (mm)", "Direction of maximum wind gust ",
            "Speed of maximum wind gust (km/h)", "9am Temperature (\u00b0C)",
            "9am relative humidity (%)", "9am cloud amount (oktas)",
            "9am MSL pressure (hPa)", "3pm Temperature (\u00b0C)",
            "3pm relative humidity (%)", "3pm cloud amount (oktas)",
            "3pm MSL pressure (hPa)",
        ])
        result = self.combine().iloc[0]
        expected = {
            "Evaporation": 3.2, "MaxGustDirection": "NW", "MaxGustSpeed": 54,
            "Temp9am": 17, "Humidity9am": 76, "Cloud9am": 7, "Pressure9am": 1023.1,
            "Temp3pm": 24, "Humidity3pm": 48, "Cloud3pm": 2, "Pressure3pm": 1021.4,
        }
        for column, value in expected.items():
            with self.subTest(column=column):
                self.assertEqual(result[column], value)

    def test_compatible_duplicates_merge_and_keep_source_filenames(self):
        self.write_month("a.csv", [["2026-01-1", 12, 30, "", 10]])
        self.write_month("b.csv", [["2026-01-1", 12, 30, 2.4, 10]])
        result = self.combine()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "Rainfall"], 2.4)
        self.assertEqual(result.loc[0, "SourceFile"], "a.csv; b.csv")

    def test_conflicting_duplicates_do_not_overwrite_output(self):
        self.write_month("a.csv", [["2026-01-1", 12, 30, 0, 10]])
        self.write_month("b.csv", [["2026-01-1", 12, 31, 0, 10]])
        self.output_file.parent.mkdir()
        self.output_file.write_text("Keep existing data", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Conflicting observations for 2026-01-01: MaxTemp"):
            self.combine()
        self.assertEqual(self.output_file.read_text(encoding="utf-8"), "Keep existing data")

    def test_missing_core_columns_raise_an_informative_error(self):
        (self.raw_directory / "bad.csv").write_text("Date,Rainfall\n2026-01-01,0\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing required columns in bad.csv"):
            self.combine()
        self.assertFalse(self.output_file.exists())

    def test_no_csv_files_raises_without_writing(self):
        with self.assertRaisesRegex(FileNotFoundError, "No CSV files"):
            self.combine()
        self.assertFalse(self.output_file.exists())


if __name__ == "__main__":
    unittest.main()
