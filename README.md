# Noongar Seasons Explorer

## 1. Project Overview

Noongar Seasons Explorer is a Python application that explores Perth weather observations in relation to the six Noongar seasons: **Birak, Bunuru, Djeran, Makuru, Djilba and Kambarang**.

Users can select a season, read a description, view weather statistics and a temperature graph, complete a quiz, and open a detailed HTML analysis report. The application uses Tkinter. Its month-based groups are an approximate teaching framework, not a complete representation of Noongar seasonal knowledge.

## 2. Project Aims

- Process Bureau of Meteorology (BOM) weather CSV files.
- Assign dates to the six seasons using the existing calendar mapping.
- Calculate seasonal weather statistics while retaining missing observations.
- Present results through a user-friendly Python GUI.
- Provide an interactive quiz and detailed analysis report.

## 3. Main Features

### Season Explorer

Select a season and click **Explore Season** to display:

- The supplied season description.
- Number of recorded days.
- Average minimum and maximum temperatures in degrees Celsius.
- Total rainfall in millimetres and average sunshine in hours per day.
- An embedded graph of daily minimum and maximum temperatures.

The application filters the saved `Season` column. Missing measurements are excluded from calculations; entirely unavailable measurements display “Not available”.

### Quiz

The **Quiz** button opens a separate window with five multiple-choice questions, four options per question, answer feedback and a final score. An answer must be selected before submission, and each question can be scored only once.

### HTML Analysis Report

**View Full Analysis Report** opens `outputs/seasons/report.html` in the default browser. It contains seasonal statistics, eight chart sets, data-coverage information and downloadable tables. A missing report produces an error message.

### Architecture Diagram

`architecture.html` provides a standalone visual overview of the system architecture, data flow, application features and supporting tests.

## 4. Data

The project contains 12 monthly BOM CSV files in `data/raw_data/`. The original preparation script, `data/combine_data.py`, cleans and combines core weather columns into `data/bom_weather.csv`.

The current analysis in `src/seasons_analysis.py` calls the enhanced `data/combine_data_extended.py` first. This retains additional weather measurements in the cleaned dataset. The analysis then exports `outputs/seasons/daily_weather_with_seasons.csv`, including the assigned `Season` column.

Both current datasets cover **1 August 2025 to 31 July 2026**:

| Check | Result |
|---|---|
| Daily records | 365 |
| Duplicate dates | 0 |
| Missing `MaxTemp` values | 1 |
| Missing `Date`, `MinTemp`, `Rainfall`, `Sunshine` or `SourceFile` values | 0 |
| Cleaned dataset columns | 21 |
| Season-labelled dataset columns | 22 |

The missing maximum temperature is retained, not filled or interpolated. Some extended measurements also contain missing values; the report documents measurement coverage.

## 5. Project Structure

Important files and folders are shown below; individual raw files and generated charts are omitted for readability.

```text
project/
├── app.py
├── data/
│   ├── raw_data/
│   ├── combine_data.py
│   ├── combine_data_extended.py
│   └── bom_weather.csv
├── src/
│   ├── data_loader.py
│   ├── seasons.py
│   └── seasons_analysis.py
├── outputs/
│   └── seasons/
│       ├── daily_weather_with_seasons.csv
│       ├── seasonal_statistics.csv
│       ├── monthly_statistics.csv
│       ├── data_quality.csv
│       ├── findings.md
│       └── report.html
├── tests/
│   ├── test_explorer.py
│   ├── test_seasons.py
│   ├── test_seasons_analysis.py
│   ├── test_data_loader.py
│   └── test_combine_data_extended.py
├── pytest.ini
├── requirements.txt
├── architecture.html
├── AI-LOG.md
└── README.md
```

## 6. Requirements

Use Python 3.10 or newer with working Tkinter/Tcl/Tk support. The latest test run used Python 3.14.7 and pytest 9.1.1. A desktop environment is required for the GUI, and a browser is needed for the HTML pages.

**Standard library:** Tkinter (`tkinter`, `ttk`, `messagebox`), `pathlib` and `webbrowser` support the GUI and file access. Processing and tests also use built-in modules such as `csv`, `argparse`, `datetime`, `unittest` and `tempfile`. These do not need pip installation. Tkinter requires the Tcl/Tk components supplied by the Python installation.

**Third-party packages:**

| Package | Purpose | Requirement |
|---|---|---|
| pandas | CSV loading and table calculations | `pandas>=2.2` |
| NumPy | Numerical operations in the analysis | `numpy>=1.26` |
| matplotlib | Analysis charts and the embedded graph | `matplotlib>=3.9` |
| pytest | Automated test discovery and execution | Required for pytest tests |

The first three packages are listed in `requirements.txt`. Pytest is installed separately for testing. Streamlit is not used.

## 7. Installation

1. Clone the repository using its actual repository URL, or download and extract the project. Keep the data and output folders with the code.
2. Open the project folder in VS Code, then select **Terminal → New Terminal**. Run commands from the folder containing `app.py`.
3. Create and activate a virtual environment in Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the project packages, plus pytest for testing:

   ```powershell
   python -m pip install -r requirements.txt
   python -m pip install pytest
   ```

5. Start the application:

   ```powershell
   python app.py
   ```

If PowerShell prevents activation, use `.\.venv\Scripts\python.exe` in place of `python` in these commands. Run tests with `.\.venv\Scripts\python.exe -m pytest` in that case.

## 8. Running the Application

From the project root:

```powershell
python app.py
```

Select a season and click **Explore Season** to update the description, summary and graph. Use **Quiz**, **View Full Analysis Report** or **Exit** for the other actions.

The application resolves its CSV and report paths relative to `app.py`. It reads existing outputs; normal GUI use does not require rerunning the analysis. Missing or unreadable weather data produces an error message.

## 9. Running the Tests

With the environment activated, run from the project root:

```powershell
pytest
```

Alternatively, use the selected Python interpreter directly:

```powershell
python -m pytest
```

Latest verified result: **69 tests collected, 69 passed, 0 failed**. Three warnings arise from existing tests that deliberately supply invalid dates to the data loader.

`tests/test_explorer.py` contains 33 cases across 16 test functions; the other test files contribute 36 cases. `pytest.ini` selects `tests/` for discovery and makes project modules available for import. Coverage includes classification, boundaries, data preparation, calculations, missing observations and report exports.

## 10. Viewing the Reports

Use **View Full Analysis Report** in the application, open the HTML files through File Explorer, or run these commands from the project root in PowerShell:

```powershell
Start-Process .\outputs\seasons\report.html
Start-Process .\architecture.html
```

Keep the whole `outputs/seasons/` folder together: the report uses adjacent chart images and downloadable tables. `architecture.html` is self-contained. Neither page needs a web server.

## 11. Data Processing Workflow

The current analysis workflow is:

```text
data/raw_data/ (monthly BOM CSV files)
    → data/combine_data_extended.py
    → data/bom_weather.csv
    → src/seasons_analysis.py
        uses src/data_loader.py and src/seasons.py
    → outputs/seasons/daily_weather_with_seasons.csv
    → app.py

src/seasons_analysis.py also exports charts, tables and report.html.
```

The analysis starts by calling the extended combiner, loads the cleaned data, adds seasons using the shared functions, calculates statistics and writes outputs. `data/combine_data.py` remains the original preparation option; running it separately writes the reduced six-column dataset. The analysis regenerates the extended dataset when it runs.

To deliberately regenerate the analysis and its saved outputs:

```powershell
python src/seasons_analysis.py
```

This rewrites `data/bom_weather.csv` and the analysis outputs. It is not needed to launch the GUI when saved files are already present.

## 12. Noongar Season Classification

`get_noongar_season(date)` in `src/seasons.py` uses this mapping:

| Season | Months |
|---|---|
| Birak | December–January |
| Bunuru | February–March |
| Djeran | April–May |
| Makuru | June–July |
| Djilba | August–September |
| Kambarang | October–November |

`add_seasons_column(df)` applies this function to `Date`. The analysis saves the labels, and the GUI filters them rather than implementing a second classification system. The lookup expects a date-like object with a month; it does not parse strings itself.

## 13. Testing and Validation

The 69 passing tests check meaningful expected results, including:

- All month mappings, season-change boundaries and leap day.
- Unsupported date inputs, invalid loader dates, empty DataFrames and missing columns.
- Seasonal means, rainfall totals, observation counts and missing-value handling.
- Dry spells, monthly summaries and wind statistics.
- Saved dataset structure, sufficient records, unique dates and consistent season labels.
- Raw-data preparation and report generation with valid local output links.

Dataset checks read saved files. Preparation and report-generation tests use temporary folders and controlled inputs, avoiding changes to the project data and report. These tests verify data and analysis behaviour; they do not constitute a complete automated test of the Tkinter interface. GUI checks and their limitations are recorded in `AI-LOG.md`.

## 14. Limitations and Data Considerations

- The dataset contains one year of Perth observations, not a long-term climate record. Seasonal totals depend on data coverage.
- Temperature, rainfall, humidity and wind are attributed to Perth Metro; sunshine, cloud and evaporation are attributed to Perth Airport. Measurement locations and observation periods differ.
- The six two-month groups are an approximate teaching and analysis framework. Weather measurements do not represent the full ecological or cultural knowledge associated with Noongar seasons.
- The analysis is descriptive, not a method for determining exact traditional season boundaries. The report includes source references and interpretation notes.
- Missing measurements remain missing. Statistics use the available observations for each measurement; unknown rainfall is not treated as zero. Wet-day, hot-day and cool-night thresholds are illustrative analysis choices, not cultural definitions.

## 15. AI Usage

AI assistance was used for planning, debugging, code suggestions, testing support and documentation. Generated code was reviewed and checked through automated tests and targeted checks; user confirmations and limits on visual GUI verification are recorded separately. See [AI-LOG.md](AI-LOG.md) for the detailed prompts, changes and verification record.

## 16. Project Documentation

- [README.md](README.md): project overview, setup and usage.
- [architecture.html](architecture.html): system architecture and data flow.
- [outputs/seasons/report.html](outputs/seasons/report.html): detailed analysis, charts and coverage.
- [AI-LOG.md](AI-LOG.md): record of AI-assisted development.

## 17. Author

Author: [Student Name]

Unit: CITS1501
