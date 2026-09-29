import pandas as pd
from pathlib import Path

#find the folder containing this Python file
data_folder = Path(__file__).resolve().parent

#find the folder containing the original BOM files
raw_data_folder = data_folder / "raw_data"

#find all CSV files
file_paths = list(raw_data_folder.glob("*.csv"))

#check that files were found
if len(file_paths) == 0:
    print("No CSV files were found.")
    print("Expected folder:", raw_data_folder)
    exit()

#store cleaned DataFrames
dataframes = []


def find_column(columns, search_text):
    """
    Find a column whose name contains the specified text.
    This helps us handle small differences between BOM CSV files.
    """

    search_text = search_text.lower().replace(" ", "")

    for column in columns:

        column_clean = str(column).lower().replace(" ", "")

        if search_text in column_clean:
            return column

    return None


#process each BOM file
for file_path in file_paths:

    print("Reading:", file_path.name)

    df = pd.read_csv(
        file_path,
        encoding="cp1252",
        skiprows=7
    )

    #remove unnecessary empty column
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    #find the columns we actually need
    date_column = find_column(df.columns, "Date")
    min_column = find_column(df.columns, "Minimum temperature")
    max_column = find_column(df.columns, "Maximum temperature")
    rainfall_column = find_column(df.columns, "Rainfall")
    sunshine_column = find_column(df.columns, "Sunshine")

    #check that important columns were found
    required_columns = {
        "Date": date_column,
        "Minimum temperature": min_column,
        "Maximum temperature": max_column,
        "Rainfall": rainfall_column,
        "Sunshine": sunshine_column
    }

    missing_columns = [
        name
        for name, column in required_columns.items()
        if column is None
    ]

    if missing_columns:
        print("WARNING - could not find:", missing_columns)
        print("Skipping:", file_path.name)
        continue

    #keep only the columns we need
    cleaned_df = df[
        [
            date_column,
            min_column,
            max_column,
            rainfall_column,
            sunshine_column
        ]
    ].copy()

    #rename them to simple names
    cleaned_df.columns = [
        "Date",
        "MinTemp",
        "MaxTemp",
        "Rainfall",
        "Sunshine"
    ]

    #add the original file name
    cleaned_df["SourceFile"] = file_path.name

    #convert Date to a proper date
    cleaned_df["Date"] = pd.to_datetime(
        cleaned_df["Date"],
        errors="coerce"
    )

    #convert weather values to numbers
    cleaned_df["MinTemp"] = pd.to_numeric(
        cleaned_df["MinTemp"],
        errors="coerce"
    )

    cleaned_df["MaxTemp"] = pd.to_numeric(
        cleaned_df["MaxTemp"],
        errors="coerce"
    )

    cleaned_df["Rainfall"] = pd.to_numeric(
        cleaned_df["Rainfall"],
        errors="coerce"
    )

    cleaned_df["Sunshine"] = pd.to_numeric(
        cleaned_df["Sunshine"],
        errors="coerce"
    )

    #add cleaned data to our list
    dataframes.append(cleaned_df)


#combine all cleaned files
combined_df = pd.concat(
    dataframes,
    ignore_index=True
)

#sort by date
combined_df = combined_df.sort_values("Date")

#reset row numbers
combined_df = combined_df.reset_index(drop=True)


# --------------------------------------------------
# DATA QUALITY CHECKS
# --------------------------------------------------

print()
print("======================================")
print("DATA QUALITY CHECK")
print("======================================")

print("Number of files:", len(file_paths))
print("Number of records:", len(combined_df))

print()
print("Columns:")
print(combined_df.columns.tolist())

print()
print("Missing values:")
print(combined_df.isna().sum())

print()
print("Duplicate dates:", combined_df["Date"].duplicated().sum())

print()
print("Date range:")
print(combined_df["Date"].min(), "to", combined_df["Date"].max())


# --------------------------------------------------
# SAVE CLEANED DATA
# --------------------------------------------------

output_file = data_folder / "bom_weather.csv"

combined_df.to_csv(
    output_file,
    index=False
)

print()
print("Cleaned dataset saved to:")
print(output_file)
