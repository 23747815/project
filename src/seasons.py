"""Calendar approximations and descriptive statistics for Noongar seasons.

The six two-month groups are a teaching aid, not a way of determining when
a traditional season begins. Those transitions follow environmental cues.
"""

import pandas as pd


SEASON_ORDER = ["Birak", "Bunuru", "Djeran", "Makuru", "Djilba", "Kambarang"]
WIND_DIRECTIONS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "Calm",
]
OPTIONAL_MEASUREMENTS = [
    "Humidity9am", "Humidity3pm", "Cloud9am", "Cloud3pm",
    "WindSpeed9am", "WindSpeed3pm", "MaxGustSpeed", "Evaporation",
]


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


def longest_dry_spell(df, threshold=1.0):
    """Return the longest observed run of days with rain below ``threshold``.

    Missing rainfall, missing dates, gaps in the daily record, and changes of
    season interrupt a run. Separate annual occurrences of a season cannot
    be joined. December and the following January are one Birak occurrence.
    Return NaN when no rainfall observations are available, and zero when
    every observed day is wet. The 1 mm threshold is an illustrative analysis
    choice, not a traditional definition of a Noongar season.
    """
    longest = 0
    current = 0
    previous_date = None
    previous_season = None
    has_observations = False

    for date, rain in df.sort_values("Date")[["Date", "Rainfall"]].itertuples(
        index=False, name=None
    ):
        if pd.isna(date) or pd.isna(rain):
            current = 0
            previous_date = None
            previous_season = None
            continue

        has_observations = True
        # Anchor Birak to its December, including January of the next year.
        season_year = date.year - (date.month == 1)
        season = (get_noongar_season(date), season_year)
        consecutive = (
            previous_date is not None
            and date - previous_date == pd.Timedelta(days=1)
            and season == previous_season
        )
        current = current + 1 if consecutive and rain < threshold else int(rain < threshold)
        longest = max(longest, current)
        previous_date = date
        previous_season = season

    return longest if has_observations else float("nan")


def seasonal_statistics(df):
    """Summarise observations in calendar order, with a row for every season.

    ``Date`` must contain datetimes; use ``add_seasons_column`` first. Missing
    measurements are excluded only from the statistic that needs them.
    Counts describe available observations, not necessarily complete seasons.
    All-missing rainfall totals and event percentages remain NaN.

    Wet days have at least 1 mm of rain, hot days have a maximum of at least
    35 degrees C, and cool nights have a minimum below 10 degrees C. These
    thresholds illustrate weather patterns; they do not define the seasons.
    ``MaxTempStd`` is the sample standard deviation of daily maxima.
    ``MeanDailyRange`` averages maximum minus minimum on the same source
    date. BOM minima cover the 24 hours ending at 9 am, while maxima cover
    the 24 hours starting at 9 am: this is not a strictly coincident diurnal
    temperature range.
    """
    rows = []
    for season in SEASON_ORDER:
        observations = df.loc[df["Season"] == season]
        minima = observations["MinTemp"].dropna()
        maxima = observations["MaxTemp"].dropna()
        rainfall = observations["Rainfall"].dropna()
        sunshine = observations["Sunshine"].dropna()
        daily_range = observations["MaxTemp"] - observations["MinTemp"]
        row = {
            "Season": season,
            "Days": len(observations),
            "TemperatureDays": len(maxima),
            "MinTemperatureDays": len(minima),
            "RainfallDays": len(rainfall),
            "SunshineDays": len(sunshine),
            "DailyRangeDays": daily_range.count(),
            "MeanMinTemp": minima.mean(),
            "MeanMaxTemp": maxima.mean(),
            "MedianMaxTemp": maxima.median(),
            "TotalRainfall": rainfall.sum(min_count=1),
            "MeanRainfall": rainfall.mean(),
            "WetDays": (rainfall >= 1).sum() if len(rainfall) else float("nan"),
            "WetDayPercent": (rainfall >= 1).mean() * 100,
            "HotDayPercent": (maxima >= 35).mean() * 100,
            "CoolNightPercent": (minima < 10).mean() * 100,
            "MeanSunshine": sunshine.mean(),
            "MeanDailyRange": daily_range.mean(),
            "MaxTempStd": maxima.std(),
            "LongestDrySpell": longest_dry_spell(observations),
        }
        for column in OPTIONAL_MEASUREMENTS:
            if column in observations:
                row[f"Mean{column}"] = observations[column].mean()
                row[f"{column}Days"] = observations[column].count()
        rows.append(row)

    return pd.DataFrame(rows).set_index("Season")


def monthly_statistics(df):
    """Return monthly means, observed rain totals, and measurement counts.

    The Date index is the first day of each month. Missing months are included
    with zero observation counts and NaN measurements, including rainfall.
    Partial-month rainfall totals are not extrapolated to a complete month.
    """
    return df.set_index("Date").resample("MS").agg(
        MeanMinTemp=("MinTemp", "mean"),
        MeanMaxTemp=("MaxTemp", "mean"),
        TotalRainfall=("Rainfall", lambda values: values.sum(min_count=1)),
        MeanSunshine=("Sunshine", "mean"),
        Days=("MaxTemp", "size"),
        MinTemperatureDays=("MinTemp", "count"),
        TemperatureDays=("MaxTemp", "count"),
        RainfallDays=("Rainfall", "count"),
        SunshineDays=("Sunshine", "count"),
    )


def wind_direction_frequencies(df, column):
    """Return percentages of valid compass directions or calm by season.

    Input directions are case insensitive; whitespace is ignored. Missing and
    unrecognised values are excluded from the denominator. A season without
    any valid direction observations has NaN in every output column.
    """
    directions = df[column].astype("string").str.strip().str.upper()
    directions = directions.replace({"CALM": "Calm"})
    valid = directions.isin(WIND_DIRECTIONS)
    counts = pd.crosstab(df.loc[valid, "Season"], directions.loc[valid])
    counts = counts.reindex(index=SEASON_ORDER, columns=WIND_DIRECTIONS, fill_value=0)
    counts.index.name = "Season"
    counts.columns.name = "Direction"
    totals = counts.sum(axis=1).replace(0, float("nan"))
    return counts.div(totals, axis=0) * 100


def wind_shift_summary(df):
    """Count morning easterly to afternoon south-westerly wind observations.

    The illustrative pattern is ENE/E/ESE at 9 am followed by SSW/SW/WSW
    at 3 pm. This is not a sea-breeze detection algorithm. Percentages use
    only days with valid observations at both times; calm is a valid
    observation but never a match. Missing and unrecognised directions are
    excluded, and case and surrounding whitespace are ignored.

    Return ``PairedWindDays``, ``EastToSWDays``, and ``EastToSWPercent`` in
    season order. A season with no valid pairs has zero counts and NaN for
    the percentage, distinguishing missing evidence from no matching days.
    """
    compass = [direction.upper() for direction in WIND_DIRECTIONS]
    morning = df["WindDirection9am"].astype("string").str.strip().str.upper()
    afternoon = df["WindDirection3pm"].astype("string").str.strip().str.upper()
    valid = morning.isin(compass) & afternoon.isin(compass)
    matches = morning.isin(["ENE", "E", "ESE"]) & afternoon.isin(["SSW", "SW", "WSW"])
    rows = []
    for season in SEASON_ORDER:
        observed = valid & (df["Season"] == season)
        count = int(observed.sum())
        matching = int((observed & matches).sum())
        rows.append({
            "Season": season,
            "PairedWindDays": count,
            "EastToSWDays": matching,
            "EastToSWPercent": 100 * matching / count if count else float("nan"),
        })
    return pd.DataFrame(rows).set_index("Season")
