# Noongar seasons and Perth weather

This educational analysis compares one year of supplied Perth weather data with
the [Bureau of Meteorology's Nyoongar calendar](https://www.bom.gov.au/resources/indigenous-weather-knowledge/indigenous-seasonal-calendars/nyoongar-calendar).
The month groups are an approximation: traditional seasons follow environmental
changes, and this small sample does not capture the full calendar's knowledge.

## Run the analysis

With Python 3.10 or newer, run these commands from the project folder:

```bash
python -m pip install -r requirements.txt
python src/seasons_analysis.py
```

Open `outputs/seasons/report.html` in your browser. It contains eight chart sets,
observed findings, downloadable tables, coverage information and source links.
Each figure is also saved as PNG and SVG for slides or assignments. Share the
whole output folder to keep the report's images and downloads together.

Each run first regenerates `data/bom_weather.csv` from the local monthly files
using `data/combine_data_extended.py`. The original `data/combine_data.py` and
raw files are preserved. The extended version retains the original columns and
adds wind, humidity, cloud, evaporation, pressure and observation-time temperatures.
Running the original combiner would produce the original reduced columns again;
running the analysis restores the extended dataset.

There is no runtime website access, no automatic package installation, and no
need for a browser server. Importing the analysis module does not rebuild data
or generate figures. To save the report elsewhere:

```bash
python -m src.seasons_analysis --output-dir outputs/my_report
```

## What the charts explore

1. Daily temperatures, rainfall and sunshine against approximate seasonal bands.
2. Temperature distributions, hot-day frequency and cool-night frequency.
3. Rainfall totals, rainfall per observed day, wet days and dry spells.
4. Sunshine, cloud cover and pan evaporation.
5. Minimum temperatures, morning/afternoon humidity, wind speeds and gusts.
6. Morning versus afternoon wind-direction distributions.
7. The mixture of warm, cool, sunny and rainy observations within each season.
8. Month-to-month changes inside and between the two-month season groups.

The report also counts a specific morning-east to afternoon-south-west wind
pattern. This illustrates a possible wind shift, not a confirmed sea breeze.

## Data and reusable functions

- `src/seasons.py` supplies season labels, seasonal/monthly statistics, dry-spell
  calculations, wind-direction frequencies and paired wind-shift counts.
- `src/data_loader.py` keeps its original complete-row behavior by default.
  The analysis uses `load_weather_data(..., drop_missing=False)` to retain valid
  rainfall or sunshine when another measurement is missing.
- `data/combine_data_extended.py` detects the CSV header below BOM metadata,
  tolerates damaged unit symbols, preserves missing values, handles calm winds,
  and rejects conflicting duplicate dates before writing the output.

Each statistic uses its own observed-data denominator. Missing rainfall is never
treated as zero. Wet days use ≥1 mm; hot days use maximum ≥35°C; cool nights use
minimum <10°C. These thresholds are chosen for demonstration. Dry runs are
clipped to one season occurrence, with December–January counted as one Birak.

The source metadata assigns temperature, rainfall, humidity and wind to Perth
Metro (009225), and sunshine, cloud and evaporation to Perth Airport (009021).
These are not all measurements at one site or over the same observation hours.
See the [Bureau's observation notes](https://www.bom.gov.au/climate/dwo/IDCJDW0000.pdf).
Sunshine duration depends on day length as well as cloud cover; relative humidity
does not directly measure dew; pan evaporation is not a soil-water balance.

The current sample covers August 2025–July 2026. If more years are added,
seasonal means pool observations and totals accumulate across years. Compare
coverage or add year-specific summaries before interpreting those totals.

## Check the calculations

```bash
python -m unittest discover -s tests -v
```

Tests use small, controlled datasets for missing observations, dry-spell breaks,
year boundaries, wind denominators, raw-data cleaning and report outputs.
AI-assisted changes and validation are recorded in `AI-LOG.md`.
