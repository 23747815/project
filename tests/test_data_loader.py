"""Run with: python -m unittest discover -s tests -v"""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data_loader import load_weather_data


class LoadWeatherDataTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.filepath = Path(directory.name) / "weather.csv"

    def load_rows(self, rows, header="Date,MinTemp,MaxTemp,Rainfall,Sunshine"):
        self.filepath.write_text(header + "\n" + "\n".join(rows), encoding="utf-8")
        return load_weather_data(self.filepath)

    def test_valid_data_is_sorted_and_values_are_preserved(self):
        result = self.load_rows([
            "2026-04-02,12.5,24.0,0.0,8.5",
            "2026-04-01,-1.5,18.0,2.4,0.0",
        ])
        expected = pd.DataFrame({
            "Date": pd.to_datetime(["2026-04-01", "2026-04-02"]),
            "MinTemp": [-1.5, 12.5],
            "MaxTemp": [18.0, 24.0],
            "Rainfall": [2.4, 0.0],
            "Sunshine": [0.0, 8.5],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_missing_or_invalid_required_values_remove_only_affected_row(self):
        valid = ["2026-04-01", "10", "20", "0", "8"]
        for column_index, column in enumerate(
            ["Date", "MinTemp", "MaxTemp", "Rainfall", "Sunshine"]
        ):
            for value in ("", "NA", "invalid", " "):
                with self.subTest(column=column, value=value):
                    invalid = valid.copy()
                    invalid[column_index] = value
                    result = self.load_rows([",".join(invalid), ",".join(valid)])
                    self.assertEqual(len(result), 1)
                    self.assertFalse(result.isna().any().any())
                    self.assertEqual(result.index.tolist(), [0])
                    self.assertEqual(result.loc[0, "Date"], pd.Timestamp("2026-04-01"))

    def test_optional_metadata_is_preserved_even_when_missing(self):
        result = self.load_rows(
            ["2026-04-01,10,20,0,8,Apr 26.csv", "2026-04-02,11,21,1,7,"],
            header="Date,MinTemp,MaxTemp,Rainfall,Sunshine,SourceFile",
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result.loc[0, "SourceFile"], "Apr 26.csv")
        self.assertTrue(pd.isna(result.loc[1, "SourceFile"]))

    def test_each_missing_required_column_raises_clear_error(self):
        columns = ["Date", "MinTemp", "MaxTemp", "Rainfall", "Sunshine"]
        for missing_column in columns:
            with self.subTest(column=missing_column):
                header = ",".join(c for c in columns if c != missing_column)
                with self.assertRaisesRegex(ValueError, f"Missing required columns: {missing_column}"):
                    self.load_rows([], header=header)

    def test_header_only_csv_returns_empty_dataframe(self):
        result = self.load_rows([])
        self.assertTrue(result.empty)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["Date"]))
        self.assertEqual(result.columns.tolist(), ["Date", "MinTemp", "MaxTemp", "Rainfall", "Sunshine"])

    def test_all_invalid_rows_return_empty_dataframe(self):
        result = self.load_rows(["bad-date,10,20,0,8", "2026-04-01,,20,0,8"])
        self.assertTrue(result.empty)

    def test_nonexistent_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_weather_data(self.filepath)

    def test_completely_empty_file_raises_empty_data_error(self):
        self.filepath.write_text("", encoding="utf-8")
        with self.assertRaises(pd.errors.EmptyDataError):
            load_weather_data(self.filepath)

    def test_keep_missing_measurements_still_removes_invalid_dates(self):
        self.filepath.write_text(
            "Date,MinTemp,MaxTemp,Rainfall,Sunshine\n"
            "2026-04-02,11,21,0,invalid\n"
            "2026-04-01,,20,,8\n"
            "invalid-date,10,20,0,8\n",
            encoding="utf-8",
        )
        result = load_weather_data(self.filepath, drop_missing=False)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.index.tolist(), [0, 1])
        self.assertTrue(pd.isna(result.loc[0, "MinTemp"]))
        self.assertTrue(pd.isna(result.loc[0, "Rainfall"]))
        self.assertEqual(result.loc[1, "Rainfall"], 0)
        self.assertTrue(pd.isna(result.loc[1, "Sunshine"]))
        self.assertEqual(result.loc[0, "Date"], pd.Timestamp("2026-04-01"))

    def test_optional_measurements_are_numeric_without_dropping_rows(self):
        result = self.load_rows(
            ["2026-04-01,10,20,0,8,invalid,65,SW", "2026-04-02,11,21,1,7,20,,"],
            header="Date,MinTemp,MaxTemp,Rainfall,Sunshine,WindSpeed3pm,Humidity3pm,WindDirection3pm",
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(pd.isna(result.loc[0, "WindSpeed3pm"]))
        self.assertEqual(result.loc[1, "WindSpeed3pm"], 20)
        self.assertTrue(pd.isna(result.loc[1, "Humidity3pm"]))
        self.assertEqual(result.loc[0, "WindDirection3pm"], "SW")


if __name__ == "__main__":
    unittest.main()
