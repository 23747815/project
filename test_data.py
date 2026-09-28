import pandas as pd

#test load BOM CSV file
df = pd.read_csv(
    "./data/Jan 26.csv",
    encoding="cp1252",
    skiprows=7
)

#remove first empty column 
df = df.drop(columns=["Unnamed: 0"])

#get rid of garbage columns
df = df[["Date",
        "Minimum temperature (ï¿½C)",
        "Maximum temperature (ï¿½C)",
        "Rainfall (mm)",
        "Sunshine (hours)"]]

#convert Date from text to datetime format
df["Date"] = pd.to_datetime(df["Date"])

#rename columns 
df = df.rename(columns={
    "Minimum temperature (ï¿½C)": "MinTemp",
    "Maximum temperature (ï¿½C)": "MaxTemp",
    "Rainfall (mm)": "Rainfall",
    "Sunshine (hours)": "Sunshine"  
}) 

#show first 5 rows 
print("\nFirst 5 rows:")
print(df.head())

#show data types
print("\nData types:")
print(df.dtypes)

#show number of records
print("\nNumber of records:", len(df))
