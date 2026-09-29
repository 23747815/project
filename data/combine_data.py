import pandas as pd
from pathlib import Path

# Find the folder where this Python file is located
data_folder = Path(__file__).resolve().parent

# The raw BOM CSV files are inside the raw_data folder
raw_data_folder = data_folder / "raw_data"

# Find all CSV files
file_paths = list(raw_data_folder.glob("*.csv"))

# Store each monthly DataFrame
dataframes = []

# Check whether any files were found
if len(file_paths) == 0:
    print("No CSV files were found.")
    print("Expected folder:", raw_data_folder)
    exit()

# Read each CSV file
for file_path in file_paths:

    print("Reading:", file_path.name)

    df = pd.read_csv(
        file_path,
        encoding="cp1252",
        skiprows=7
    )

    # Remove unnecessary empty column
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Convert Date to a proper date
    df["Date"] = pd.to_datetime(df["Date"])

    # Rename columns we will use
    df = df.rename(columns={
        "Minimum temperature (ï¿½C)": "MinTemp",
        "Maximum temperature (ï¿½C)": "MaxTemp",
        "Rainfall (mm)": "Rainfall",
        "Sunshine (hours)": "Sunshine"
    })

    dataframes.append(df)


# Combine all monthly files
combined_df = pd.concat(dataframes, ignore_index=True)

# Sort by date
combined_df = combined_df.sort_values("Date")

# Reset row numbers
combined_df = combined_df.reset_index(drop=True)

# Display information
print()
print("Number of files:", len(file_paths))
print("Total number of records:", len(combined_df))

print()
print("First 5 records:")
print(combined_df.head())

print()
print("Last 5 records:")
print(combined_df.tail())

# Save the combined dataset inside the data folder
output_file = data_folder / "bom_weather.csv"

combined_df.to_csv(output_file, index=False)

print()
print("Combined dataset saved to:", output_file)
