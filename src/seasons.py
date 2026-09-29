def get_noongar_season(date):
    """Return the Noongar season for a given date.

    Accepts a datetime.date, datetime.datetime, or pandas.Timestamp.
    Months provide an approximate guide; traditional seasons follow
    environmental changes rather than fixed calendar dates.

    The month mapping is:
        - Birak: December to January
        - Bunuru: February to March
        - Djeran: April to May
        - Makuru: June to July
        - Djilba: August to September
        - Kambarang: October to November
    """
    seasons_by_month = {
        1: "Birak",
        2: "Bunuru",
        3: "Bunuru",
        4: "Djeran",
        5: "Djeran",
        6: "Makuru",
        7: "Makuru",
        8: "Djilba",
        9: "Djilba",
        10: "Kambarang",
        11: "Kambarang",
        12: "Birak",
    }
    return seasons_by_month[date.month]

def add_seasons_column(df):
    """Add a 'Season' column to a DataFrame based on the 'Date' column.

    The 'Season' column will contain the Noongar season corresponding to
    each date in the 'Date' column. The function assumes that the 'Date'
    column is of type datetime.date, datetime.datetime, or pandas.Timestamp.
    """
    df["Season"] = df["Date"].apply(get_noongar_season)
    return df

def seasonal_average(df, column):
    """Calculate the average weather measurement for each Noongar season.

    Returns a DataFrame with the average values for each season.
    The input DataFrame must contain 'Season' and the specified column.
    """
    return df.groupby("Season")[column].mean().reset_index(name=f"Average{column}")

def seasonal_summary(df):
    """Generate a summary of average weather measurements for each Noongar season.

    Returns a DataFrame with the average MinTemp, MaxTemp, Rainfall, and Sunshine
    for each season. The input DataFrame must contain 'Season' and the relevant
    weather measurement columns.
    """
    summary = df.groupby("Season").agg({
        "MinTemp": "mean",
        "MaxTemp": "mean",
        "Rainfall": "mean",
        "Sunshine": "mean"
    }).reset_index()
    summary.columns = ["Season", "AverageMinTemp", "AverageMaxTemp", "AverageRainfall", "AverageSunshine"]
    return summary