"""Combine BOM daily observations, retaining fields useful for seasonal analysis.

This is an enhanced adaptation of combine_data.py; the original is preserved.
The source files describe a mixture of Perth Metro (temperature, humidity,
wind, pressure, rainfall) and Perth Airport (cloud, evaporation, sunshine).
Missing observations stay missing: they must not become dry or calm days.
Importing this module does not read or write any files.
"""

import csv
from io import StringIO
from pathlib import Path

import pandas as pd


# Match the descriptive part of the BOM header, so damaged degree symbols or
# changed units formatting do not prevent the column from being recognised.
COLUMN_NAMES = {
    "Date": "Date",
    "MinTemp": "Minimum temperature",
    "MaxTemp": "Maximum temperature",
    "Rainfall": "Rainfall",
    "Sunshine": "Sunshine",
    "Evaporation": "Evaporation",
    "MaxGustSpeed": "Speed of maximum wind gust",
    "MaxGustDirection": "Direction of maximum wind gust",
    "Temp9am": "9am Temperature",
    "Humidity9am": "9am relative humidity",
    "Cloud9am": "9am cloud amount",
    "WindDirection9am": "9am wind direction",
    "WindSpeed9am": "9am wind speed",
    "Pressure9am": "9am MSL pressure",
    "Temp3pm": "3pm Temperature",
    "Humidity3pm": "3pm relative humidity",
    "Cloud3pm": "3pm cloud amount",
    "WindDirection3pm": "3pm wind direction",
    "WindSpeed3pm": "3pm wind speed",
    "Pressure3pm": "3pm MSL pressure",
}
REQUIRED_COLUMNS = ("Date", "MinTemp", "MaxTemp", "Rainfall", "Sunshine")
WIND_COLUMNS = (
    ("MaxGustSpeed", "MaxGustDirection"),
    ("WindSpeed9am", "WindDirection9am"),
    ("WindSpeed3pm", "WindDirection3pm"),
)
DIRECTION_COLUMNS = {direction for _, direction in WIND_COLUMNS}


def _normalise_header(value):
    return "".join(str(value).lower().split())


def _read_weather_file(file_path):
    """Find the table below BOM's metadata and clean one month's observations."""
    try:
        text = file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = file_path.read_text(encoding="cp1252")

    # Metadata length can vary. Locate the actual Date header instead of
    # assuming that every monthly download needs the same skiprows value.
    lines = text.splitlines()
    header_line = next(
        (number for number, line in enumerate(lines)
         if "date" in [_normalise_header(cell)
                       for cell in next(csv.reader([line]), [])]),
        None,
    )
    if header_line is None:
        raise ValueError(f"No Date header found in {file_path.name}")

    raw = pd.read_csv(StringIO("\n".join(lines[header_line:])), dtype=str)
    source_columns = {}
    for name, description in COLUMN_NAMES.items():
        source_columns[name] = next(
            (column for column in raw.columns
             if _normalise_header(column).startswith(_normalise_header(description))),
            None,
        )
    missing = [name for name in REQUIRED_COLUMNS if source_columns[name] is None]
    if missing:
        raise ValueError(
            f"Missing required columns in {file_path.name}: {', '.join(missing)}"
        )

    cleaned = pd.DataFrame(index=raw.index)
    for name, source in source_columns.items():
        cleaned[name] = raw[source] if source is not None else float("nan")
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], format="%Y-%m-%d", errors="coerce")

    for name in DIRECTION_COLUMNS:
        cleaned[name] = cleaned[name].astype("string").str.strip().str.upper()
        cleaned[name] = cleaned[name].replace("", pd.NA)

    for speed, _ in WIND_COLUMNS:
        # BOM puts 'Calm' in the speed field and leaves direction blank.
        cleaned[speed] = (
            cleaned[speed].astype("string").str.strip().str.upper().replace("CALM", "0")
        )

    for name in COLUMN_NAMES:
        if name != "Date" and name not in DIRECTION_COLUMNS:
            cleaned[name] = pd.to_numeric(cleaned[name], errors="coerce")

    for speed, direction in WIND_COLUMNS:
        calm = cleaned[speed].eq(0)
        cleaned.loc[calm, direction] = "CALM"

    cleaned["SourceFile"] = file_path.name
    # A missing measurement does not invalidate the other observations that day.
    return cleaned.dropna(subset=["Date"])


def combine_weather_data(raw_data_folder=None, output_file=None):
    """Return and save a chronologically ordered daily weather DataFrame.

    Defaults read data/raw_data/*.csv and write data/bom_weather.csv, relative
    to this module. Optional weather columns are filled with missing values.
    Overlapping dates are merged when their observed values agree (including
    complementary missing fields), recording every source filename. Conflicting
    observations raise ValueError before the output file is touched.
    """
    data_folder = Path(__file__).resolve().parent
    raw_data_folder = Path(raw_data_folder) if raw_data_folder is not None else data_folder / "raw_data"
    output_file = Path(output_file) if output_file is not None else data_folder / "bom_weather.csv"
    file_paths = sorted(raw_data_folder.glob("*.csv"))
    if not file_paths:
        raise FileNotFoundError(f"No CSV files found in {raw_data_folder}")

    combined = pd.concat([_read_weather_file(path) for path in file_paths], ignore_index=True)
    if combined.empty:
        raise ValueError("No valid dated observations found in the raw CSV files")

    duplicates = combined[combined["Date"].duplicated(keep=False)]
    if not duplicates.empty:
        value_columns = [name for name in COLUMN_NAMES if name != "Date"]
        for date, observations in duplicates.groupby("Date"):
            conflicts = observations[value_columns].nunique(dropna=True).gt(1)
            if conflicts.any():
                names = ", ".join(conflicts[conflicts].index)
                raise ValueError(f"Conflicting observations for {date:%Y-%m-%d}: {names}")
        sources = combined.groupby("Date")["SourceFile"].agg(
            lambda values: "; ".join(dict.fromkeys(values))
        )
        combined = combined.groupby("Date", as_index=False).first()
        combined["SourceFile"] = combined["Date"].map(sources)

    # Keep the original six columns first, for familiarity and compatibility.
    output_columns = [*REQUIRED_COLUMNS, "SourceFile"]
    output_columns.extend(name for name in COLUMN_NAMES if name not in REQUIRED_COLUMNS)
    combined = combined[output_columns].sort_values("Date").reset_index(drop=True)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_file, index=False)
    return combined


if __name__ == "__main__":
    weather = combine_weather_data()
    print(f"Saved {len(weather)} daily observations to data/bom_weather.csv")
    print("Missing observations by column:")
    print(weather.isna().sum().to_string())
