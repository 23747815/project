import pandas as pd


def load_weather_data(filepath):
    """Load a combined weather CSV and return complete observations.

    Rows with missing or invalid dates or weather measurements are removed.
    Extra columns, such as SourceFile, are preserved and may contain missing
    values. The returned DataFrame is sorted by date with a fresh index.
    """
    df = pd.read_csv(filepath)
    weather_columns = ["MinTemp", "MaxTemp", "Rainfall", "Sunshine"]
    required_columns = ["Date", *weather_columns]

    missing_columns = [column for column in required_columns if column not in df]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for column in weather_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=required_columns)
    return df.sort_values("Date").reset_index(drop=True)
