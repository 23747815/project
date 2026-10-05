#AI use log 

AI used | purpose/prompt | what was used | reviewed

## 28/09/2026 

### project planning and application design
*ChatGPT | asked for guidance on app design | designed structure of app using Aus BOM weather data | accepted suggested structure, features, analysis 

### BOM data and pandas 
*ChatGPT | asked how to load and inspect BOM CSV files using python and pandas | provided python code for reading CSV, skipping metadata rows, checking dataset | pandas 'read_csv()', removed unnecessary columns, column names, data types, check BOM data loaded correctly 

### data cleaning 
*ChatGPT | asked for help preparing BOM data | suggested converting date column to datetime, simplifying names | date conversion, renamed columns 

## 29/09/2026 

### Choice of application technology
- **AI tool:** ChatGPT
- **Purpose:** Asked whether Streamlit was required for the project.
- **What AI was used for:** Reviewed the assignment requirements and explained that the brief requires an interactive application with at least three screens/views, but does not specify Streamlit.
- **What was used:** Decided to develop the application using Python and Tkinter instead of Streamlit.
- **Verification/actions:** Decision was based on the assignment requirements and the team's preference to avoid an unnecessary framework.

### Combining BOM datasets
- **AI tool:** ChatGPT
- **Purpose:** Asked how to combine multiple monthly BOM CSV files into one dataset.
- **What AI was used for:** Provided Python code using Pandas to load multiple CSV files, clean the relevant columns, convert dates, combine the datasets and save the result.
- **What was used:** `glob`, `pandas`, `pd.concat()`, date conversion, column standardisation and CSV output.
- **Verification/actions:** Ran the program in VS Code. Confirmed that 12 monthly BOM files were successfully processed and produced 365 records.

### Debugging file paths
- **AI tool:** ChatGPT
- **Purpose:** Asked for help after the dataset-combining program returned `ValueError: No objects to concatenate`.
- **What AI was used for:** Helped identify that the Python script and `raw_data` folder were in different locations from the paths originally used.
- **What was used:** Revised the file-path handling and used `Path(__file__)` so the program could locate the `raw_data` folder relative to the Python script.
- **Verification/actions:** Ran the revised program successfully and confirmed that all 12 files were found.

### Data cleaning and quality checking
- **AI tool:** ChatGPT
- **Purpose:** Asked how to handle differences between the monthly BOM files.
- **What AI was used for:** Suggested selecting only the weather variables needed by the application and standardising their names rather than keeping unnecessary columns.
- **What was used:** The combined dataset was reduced to Date, MinTemp, MaxTemp, Rainfall, Sunshine and SourceFile.
- **Verification/actions:** Ran data-quality checks and confirmed:
  - 12 files
  - 365 records
  - no duplicate dates
  - date range from 2025-08-01 to 2026-07-31
  - 1 missing MaxTemp value
- **Result:** The cleaned dataset was saved as `bom_weather.csv`.

### AI documentation
- **AI tool:** ChatGPT
- **Purpose:** Asked how to maintain the required `AI-LOG.md`.
- **What AI was used for:** Explained what significant AI use should be recorded and how to document prompts, uses, verification and changes.
- **What was used:** Created the structure and entries in this AI log.
- **Verification/actions:** Ensured the log reflects actual AI-assisted work undertaken during the project.

### Weather data loader
*Codex | requested a reusable load_weather_data(filepath) function | added src/data_loader.py to read combined CSV data, convert dates and measurements, reject missing required columns, remove incomplete or invalid observations, and sort by date | verified against data/bom_weather.csv: 364 clean rows returned

### Weather data loader tests
*Codex | requested tests with a variety of data | added tests/test_data_loader.py using unittest and temporary CSV files; covers valid values and sorting, missing and invalid required values, optional metadata, missing columns, header-only and invalid-only data, nonexistent files, and empty files | python -m unittest discover -s tests -v: all 8 tests passed; pandas emitted date-format inference warnings for malformed-date cases

### Ongoing AI change summaries
Record summaries of subsequent AI-assisted project changes in this file, as requested by the user.

### Noongar season lookup
- **AI tool:** Codex
- **Purpose:** Fill out the existing get_noongar_season(date) stub.
- **What was used:** Added a month-to-season lookup in src/seasons.py, accepting Python dates, datetimes and pandas Timestamps. Documented that month boundaries are approximate guides to traditional seasons.
- **Source:** [Bureau of Meteorology seasonal calendar](https://media.bom.gov.au/social/blog/53/nyoongar-seasonal-calendar/).
- **Verification/actions:** Checked all 12 month mappings, a datetime at year end, and a pandas Timestamp on leap day; all checks passed.

### Educational weather analysis and graphs
- **AI tool:** Codex, with parallel agents for data preparation, seasonal statistics and an independent review.
- **Purpose:** Add a variety of analyses and graphs demonstrating the relationship between Noongar seasons and the supplied Perth weather observations, inspired by the Bureau's calendar.
- **Sources:** [Bureau Nyoongar seasonal calendar](https://www.bom.gov.au/resources/indigenous-weather-knowledge/indigenous-seasonal-calendars/nyoongar-calendar), [Bureau observation notes](https://www.bom.gov.au/climate/dwo/IDCJDW0000.pdf), and metadata in the local raw CSV files.
- **What was used:** Implemented src/seasons_analysis.py with eight chart sets: daily timelines, temperature distributions and threshold frequencies, rainfall and dry spells, sunshine/cloud/evaporation, cooler mornings and humidity, morning/afternoon winds, the mixture of daily weather, and monthly transitions. Each run exports PNG/SVG figures, CSV tables, findings.md and an HTML report under outputs/seasons.
- **Reusable calculations:** Extended src/seasons.py with seasonal/monthly statistics, observed-data counts, dry spells, wind-direction percentages and paired morning-east/afternoon-south-west counts. Existing helper functions remain available.
- **Data preparation:** Added data/combine_data_extended.py as an enhanced adaptation of the original combiner, retaining wind, humidity, cloud, evaporation, pressure and observation-time temperature fields. The analysis regenerates data/bom_weather.csv at the start of each run. Original combiner and raw files were preserved. Metadata/header differences, calm wind values and compatible/conflicting duplicate dates are handled explicitly.
- **Missing data:** Added the backward-compatible drop_missing=False option to load_weather_data. The analysis retains all dated rows and uses each measurement's available observations; it does not fill missing weather values or count missing rainfall as zero.
- **Documentation:** Added README.md with run/test instructions, requirements.txt, and ignore rules for future Python cache files and virtual environments. Report text explains the approximate month mapping, one-year sample, mixed stations, observation windows, illustrative thresholds and limits of wind/humidity proxies.
- **Findings:** The sample has 365 dates from August 2025 through July 2026. Birak's mean maximum is 31.17°C versus Bunuru's 30.96°C; Djilba has 302.4 mm of rain versus Makuru's 178.4 mm. These departures from the broad descriptions are retained. Djeran shows cooler, more humid mornings; Kambarang is warmer than Djilba and has a longer observed dry run.
- **Verification/actions:** All 36 tests passed, including full report generation with sparse data and entirely missing optional winds, local report-link checks, missing-value denominators, year/season boundaries and raw CSV handling. Ran the full analysis against the supplied data and visually inspected the exported figures. Confirmed the original six CSV columns are unchanged and all 365 unique dates are retained; the expanded CSV has 21 columns. Missing measurements remain: one maximum temperature, three evaporation values and two gust records. Existing malformed-date loader tests still emit pandas date-format inference warnings; they pass.
