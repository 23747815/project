import pandas as pd

#test load BOM CSV file
df = pd.read_csv(
    "./data/Jan 26.csv",
    encoding="cp1252",
    skiprows=7
)

#remove first empty column 
df = df.drop(columns=["Unnamed: 0"])

print(df)

#checking number of records
print("Number of records:", len(df))

#checking what data we have 
print("\nColumns")
print(df.columns.tolist())

#filtering out unnecessary columns 
print(
    df[
        [
            "Date",
            "Minimum temperature (ï¿½C)",
            "Maximum temperature (ï¿½C)",
            "Rainfall (mm)", 
            "Sunshine (hours)",
        ]
    ]
)

#checking data types
print("\nData types")
print(df.dtypes)
