import pandas as pd

#test load BOM CSV file
df = pd.read_csv(
    "./data/Jan 26.csv",
    encoding="cp1252",
    skiprows=7
)

#remove first empty column 
df = df.drop(columns=["Unnamed: 0"])

#convert Date from text to datetime format
df["Date"] = pd.to_datetime(df["Date"])

#rename columns 
df = df.rename(columns={
    "Minimum temperature (°C)": "MinTemp",
    "Maximum temperature (°C)": "MaxTemp",
    "Rainfall (mm)": "Rainfall",
    "Sunshine (hours)": "Sunshine"  
})