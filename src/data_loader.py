import pandas as pd


def load_weather_data(filepath, *, drop_missing=True):
    """Load a combined weather CSV, converting dates and weather measurements.

    By default, rows missing any of the four original weather measurements are
    removed, preserving the original behaviour. With drop_missing=False, keep
    those rows so each analysis can use every available observation of its own
    variable. Invalid dates are always removed; no values are filled or guessed.
    Extra columns, such as SourceFile, are preserved. Optional measurements may
    be missing in either mode. The result is sorted by date with a fresh index.
    """
    df = pd.read_csv(filepath)
    weather_columns = ["MinTemp", "MaxTemp", "Rainfall", "Sunshine"]
    required_columns = ["Date", *weather_columns]

    missing_columns = [column for column in required_columns if column not in df]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    optional_numeric_columns = [
        "Evaporation", "MaxGustSpeed", "Temp9am", "Humidity9am", "Cloud9am",
        "WindSpeed9am", "Pressure9am", "Temp3pm", "Humidity3pm", "Cloud3pm",
        "WindSpeed3pm", "Pressure3pm",
    ]
    for column in weather_columns + [c for c in optional_numeric_columns if c in df]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=required_columns if drop_missing else ["Date"])
    return df.sort_values("Date").reset_index(drop=True)
