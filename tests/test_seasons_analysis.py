"""Exercise report generation with sparse data and absent optional winds."""

from contextlib import redirect_stdout
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import matplotlib.pyplot as plt
import pandas as pd

from src import seasons_analysis
from src.seasons import OPTIONAL_MEASUREMENTS, add_seasons_column, seasonal_statistics, wind_shift_summary


class ReportLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for attribute, value in attrs:
            if attribute in ("href", "src") and value and not value.startswith(("http", "#")):
                self.paths.append(value)


def sample_weather():
    frame = pd.DataFrame({
        "Date": pd.date_range("2025-08-01", periods=12, freq="MS"),
        "MinTemp": [10.0] * 12,
        "MaxTemp": [25.0] * 11 + [float("nan")],
        "Rainfall": [0.0, 2.0] * 6,
        "Sunshine": [8.0] * 12,
        "SourceFile": ["example.csv"] * 12,
    })
    for column in OPTIONAL_MEASUREMENTS:
        frame[column] = float("nan")
    # This is the dtype produced when a whole optional CSV column is empty.
    frame["WindDirection9am"] = float("nan")
    frame["WindDirection3pm"] = float("nan")
    return frame


class AnalysisTests(unittest.TestCase):
    def test_report_exports_all_figures_and_valid_local_links(self):
        frame = sample_weather()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            # Test the actual analysis and drawing, while avoiding a write to
            # the user's combined dataset during a unit-test run.
            with patch.object(seasons_analysis, "combine_weather_data") as rebuild:
                with patch.object(seasons_analysis, "load_weather_data", return_value=frame) as load:
                    with redirect_stdout(StringIO()):
                        seasons_analysis.run_analysis(output)
            rebuild.assert_called_once_with()
            self.assertFalse(load.call_args.kwargs["drop_missing"])
            self.assertEqual(len(list(output.glob("*.png"))), 8)
            self.assertEqual(len(list(output.glob("*.svg"))), 8)
            self.assertTrue(all(path.stat().st_size > 1000 for path in output.glob("*.png")))
            links = ReportLinks()
            links.feed((output / "report.html").read_text(encoding="utf-8"))
            self.assertGreater(len(links.paths), 20)
            for path in links.paths:
                with self.subTest(path=path):
                    self.assertTrue((output / path).is_file())
            exported = pd.read_csv(output / "daily_weather_with_seasons.csv")
            self.assertEqual(len(exported), 12)
            self.assertEqual(exported.MaxTemp.isna().sum(), 1)
            self.assertEqual(plt.get_fignums(), [])

    def test_headline_explains_wholly_missing_temperature(self):
        frame = add_seasons_column(sample_weather())
        frame["MaxTemp"] = float("nan")
        findings = seasons_analysis.build_findings(seasonal_statistics(frame), wind_shift_summary(frame))
        self.assertIn("insufficient", findings[0])

    def test_coverage_counts_measurements_independently(self):
        coverage = seasons_analysis.data_quality(sample_weather())
        self.assertEqual(coverage.loc["MaxTemp", "ObservedDays"], 11)
        self.assertEqual(coverage.loc["Rainfall", "ObservedDays"], 12)
        self.assertEqual(coverage.loc["WindDirection9am", "MissingDays"], 12)


if __name__ == "__main__":
    unittest.main()
