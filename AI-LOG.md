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

## 05/10/2026

### Basic tkinter application
- **AI tool:** Codex
- **Purpose:** Create a beginner-friendly main GUI for Noongar Seasons Explorer without repeating the weather analysis.
- **What was used:** Added app.py with a heading, introduction, six-season dropdown, selected-season message, temporary quiz message and Exit button. Uses only Python's tkinter/ttk and messagebox.
- **GUI details:** The window title and heading are "Noongar Seasons Explorer". The "Select a season:" dropdown contains Birak, Bunuru, Djeran, Makuru, Djilba and Kambarang, defaults to Birak and only allows selection from the list.
- **Button behaviour:** "Explore Season" displays the selected season in a message box; "Quiz" displays "Quiz coming soon!"; "Exit" closes the application.
- **Code explanation:** Explained the design before editing and added beginner-friendly comments covering the main function, StringVar selection, button callbacks and tkinter event loop. Provided the VS Code terminal command `python app.py`.
- **Scope:** No Streamlit or additional libraries were added. Weather analysis, quiz questions and cultural information were not implemented in the GUI.
- **Verification/actions:** Reviewed the code and callbacks. Runtime verification was unavailable because this environment could not execute the installed python or py command aliases. Existing CSV files, analysis code and HTML report were not changed.

### Inspection of existing season-labelled weather data
- **AI tool:** Codex
- **Purpose:** Locate the existing daily weather export and season-assignment logic before connecting weather data to the GUI, avoiding a second classification system.
- **Findings:** run_analysis() in src/seasons_analysis.py calls add_seasons_column() and writes daily_weather_with_seasons.csv using df.to_csv(..., index=False). The default export location is outputs/seasons/daily_weather_with_seasons.csv, and the existing HTML report links to it.
- **Existing logic:** src/seasons.py defines get_noongar_season(date), which maps December-January to Birak, February-March to Bunuru, April-May to Djeran, June-July to Makuru, August-September to Djilba and October-November to Kambarang. add_seasons_column(df) applies this function to Date and stores the result in Season. The code documents these month groups as approximations.
- **Export columns:** Date, MinTemp, MaxTemp, Rainfall, Sunshine, SourceFile, Evaporation, MaxGustSpeed, MaxGustDirection, Temp9am, Humidity9am, Cloud9am, WindDirection9am, WindSpeed9am, Pressure9am, Temp3pm, Humidity3pm, Cloud3pm, WindDirection3pm, WindSpeed3pm, Pressure3pm, Season.
- **Verification/actions:** Inspected source code, the HTML download link and the saved CSV. Confirmed 22 columns and 365 daily records, with all six season labels present. Did not rerun analysis or modify application code, data or report files; only this log was updated.
- **Proposed reuse:** The GUI can read the existing export's Season column. If new dates require classification, import the existing functions from src.seasons rather than duplicate the month mapping. GUI integration has not been implemented.

### Connecting existing weather data to the GUI
- **AI tool:** Codex
- **Purpose:** Make Explore Season display a weather summary using the existing season-labelled CSV.
- **What was used:** Updated app.py to load outputs/seasons/daily_weather_with_seasons.csv with pandas.read_csv() when Explore Season is clicked. The path is resolved relative to app.py. Rows are filtered using the saved Season column, without assigning seasons again.
- **Summary calculations:** Counts matching records, calculates mean minimum temperature, mean maximum temperature and mean sunshine, and sums rainfall. Numeric conversion occurs in memory only. Missing values are excluded; sum(min_count=1) prevents entirely missing rainfall from displaying as zero. Unavailable measurements display "Not available".
- **Error handling:** Added messages for missing or unreadable CSV files, missing required columns and seasons with no records. Previous results are cleared before loading.
- **Verification/actions:** Syntax and tkinter/pandas import checks passed using the installed Python executable directly. Automated GUI execution was blocked by a missing Tcl runtime. The user subsequently confirmed that the application loaded the CSV and displayed the summaries correctly.
- **Scope:** Only app.py was modified for this implementation. No CSV files, HTML report or src/seasons.py changes were made, and the existing analysis was not rerun. Quiz remained a placeholder and Exit retained its behaviour.

### Embedded daily temperature graph
- **AI tool:** Codex
- **Purpose:** Add one temperature visualisation to the Explore Season results.
- **What was used:** Added a matplotlib Figure embedded in Tkinter with FigureCanvasTkAgg. The graph plots daily minimum and maximum temperatures against Date, with temperature in degrees Celsius, a legend and date labels.
- **Data and updates:** Uses the same filtered season records as the summary. Dates are converted and sorted in an in-memory copy. Each Explore Season click clears and redraws the existing graph; no separate plot window is opened. Missing temperatures remain gaps, and empty or unplottable data produces a helpful message.
- **Verification/actions:** Syntax and import checks passed. Non-GUI rendering checks passed for all six seasons, plotted values, graph replacement, empty data, missing temperatures and invalid dates. Full Tkinter visual testing was unavailable because of the local Tcl runtime issue. The user subsequently reported that the summary and graph appeared correctly, but Quiz and Exit disappeared after exploring a season.
- **Scope:** Modified only app.py; preserved the existing season labels, calculations, CSV files, HTML report and src/seasons.py.

### Fixing control-button visibility
- **AI tool:** Codex
- **Purpose:** Keep Explore Season, Quiz and Exit accessible when the weather results expand.
- **Cause and change:** Quiz and Exit were packed after the summary and graph in the same frame, allowing growing results to consume the available vertical space. Moved all three buttons into a controls frame packed before a separate expandable results area containing the summary and graph.
- **Verification/actions:** Syntax and whitespace checks passed. Compared callback function syntax trees with the previous version and confirmed that calculation, graph and button callback functions were unchanged. Visual confirmation of the layout fix remains pending because the local Tcl runtime prevented GUI execution.
- **Scope:** Only app.py was changed for the fix. No weather calculations, graph logic, data files, HTML report or src/seasons.py were modified.

### First working multiple-choice quiz
- **AI tool:** Codex
- **Purpose:** Replace the "Quiz coming soon!" placeholder with a five-question quiz while preserving the existing main window and weather features.
- **What was used:** Replaced show_quiz() in app.py with a separate Tkinter Toplevel window. Each question has four radio-button choices, a Submit Answer button, feedback and a Next Question button. The final question provides Show Results, followed by the final score and a Close Quiz button. The main window remains usable.
- **Quiz content:** Used only the season facts supplied by the user: Birak's December-January months and the described weather for Bunuru, Djeran, Makuru and Djilba. Answer choices include the six season names; no additional cultural claims were introduced.
- **Answer handling:** Requires a selection before submission, awards one point for a correct answer, shows the correct answer after an incorrect response, and locks submitted choices to prevent repeated scoring. Each question starts with no answer selected. Each new quiz window starts a fresh score.
- **Verification/actions:** Python syntax and whitespace checks passed. In-memory callback checks using simulated widgets covered unanswered submissions, question progression, four distinct choices, correct/incorrect feedback, repeated-submit protection, final scores of 0/5, 4/5 and 5/5, and closing/reopening. These checks did not exercise real Tkinter rendering; visual GUI testing remains unverified because of the local Tcl runtime issue.
- **Scope:** Only app.py was modified for the implementation. A syntax-tree comparison confirmed that all code outside show_quiz() was unchanged, including the main layout, weather calculations and temperature graph. CSV files, the HTML report and src/seasons.py were untouched; no new files or libraries were added.

### Season information in Explore Season results
- **AI tool:** Codex
- **Purpose:** Display a short description of the selected season alongside the existing weather results.
- **What was used:** Added a season_descriptions dictionary in app.py containing the six descriptions exactly as supplied by the user. Added a wrapped, left-aligned "About this season" section inside the existing results area, above the weather summary and below the separate controls area.
- **Behaviour:** Each Explore Season click updates a StringVar with the selected season's description. The description updates even if weather data cannot be loaded. The dictionary is used for display only; it does not assign seasons to records.
- **Content limits:** Used only the supplied month ranges and weather descriptions. No additional Noongar cultural information, traditions, stories or ecological claims were introduced.
- **Verification/actions:** Python syntax and whitespace checks passed. In-memory checks confirmed description updates and successful weather-summary and graph execution for all six seasons. Code comparisons confirmed that the weather calculations, graph functions, quiz and main button layout were unchanged. Real Tkinter rendering and button visibility were not retested because of the existing Tcl runtime issue.
- **Scope:** Only app.py was modified for this implementation. CSV files, the HTML report and src/seasons.py were untouched. No new libraries or files were added.

### Opening the full analysis report from the GUI
- **AI tool:** Codex
- **Purpose:** Add a "View Full Analysis Report" button that opens the existing HTML report in the user's default browser.
- **What was used:** Added the button to the existing controls frame and a dedicated open_report() function in app.py. The function uses pathlib to resolve outputs/seasons/report.html relative to app.py, checks is_file(), converts the path to a file URL with as_uri(), and calls Python's built-in webbrowser.open().
- **Error handling:** If the report is missing, a Tkinter error message explains that the analysis report could not be found and shows the expected path.
- **Verification/actions:** Python syntax and whitespace checks passed. Confirmed that the report exists. Tests with mocked browser and message-box calls verified the expected report URL and missing-file error, without launching a browser. A syntax-tree comparison confirmed that the existing application code was unchanged apart from the new import, function and button. Actual button visibility and browser launching remain unverified in this environment.
- **Scope:** Only app.py was modified for the implementation. Weather calculations, the temperature graph, quiz, season descriptions and existing controls were preserved. The HTML report, CSV files and src/seasons.py were not modified. No external dependencies were added.
