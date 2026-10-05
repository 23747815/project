# Windows deployment

The application is packaged as a **Windows x64 folder**, not a single file.
Recipients do not need Python, VS Code or pip. They need Windows and a browser
to view the report. Distribute the entire `dist/NoongarSeasonsExplorer/` folder.

## Build

From the project root in Windows PowerShell, using a working Python installation
with Tkinter (the recorded build uses Python 3.14.7 x64):

```powershell
python -m venv .build-venv
.\.build-venv\Scripts\python.exe -m pip install -r deployment/requirements-build.txt
.\build_deployment.ps1 -Python .\.build-venv\Scripts\python.exe
```

The script checks runtime assets and Tkinter before calling PyInstaller. It does
not regenerate the data or HTML report. It writes temporary build files under
`build/`, then creates:

```text
dist/NoongarSeasonsExplorer/
    NoongarSeasonsExplorer.exe
    README.txt
    _internal/
        outputs/seasons/        # CSV, HTML, charts and downloads
        ...                     # Bundled Python, packages and Tcl/Tk runtime
```

The equivalent PyInstaller command, run from the project root, is:

```powershell
python -m PyInstaller --noconfirm --clean --onedir --windowed --name NoongarSeasonsExplorer --distpath dist --workpath build/pyinstaller --specpath build --add-data "${PWD}/outputs/seasons:outputs/seasons" --runtime-hook "${PWD}/deployment/verify_packaged_hook.py" --exclude-module pytest --exclude-module IPython --exclude-module notebook app.py
```

Use the script for its preflight checks and Tcl/Tk handling. Python 3.14's Tcl/Tk
scripts may be embedded in the runtime DLLs. `deployment/prepare_tk.py` extracts
those archives into `deployment/toolchain/libraries/` when present. The build
uses those paths; recipients do not need that build-time folder or environment
variables. A normal installation with separate Tcl/Tk libraries uses its own
libraries. No system Python files are changed.

`app.py` is unchanged. Its `Path(__file__).resolve().parent` paths resolve to
PyInstaller's bundle directory, where `--add-data` preserves `outputs/seasons/`.
See [PyInstaller runtime paths](https://www.pyinstaller.org/en/stable/runtime-information.html).

## Runtime contents

- `app.py` is compiled into the executable's application archive.
- pandas, NumPy, matplotlib, Tkinter/Tcl/Tk, Python and native dependencies are bundled.
- The existing `daily_weather_with_seasons.csv` and full report folder are included.
- The report has inline CSS and local PNG images, SVG downloads and CSV links.
  Its external BOM source links remain web links, not required application assets.
- Raw BOM files, data-preparation scripts, `src/`, tests, `.git`, development
  caches, architecture documentation and build tools are not project runtime inputs.

`deployment/check_runtime.py` checks all local HTML `src`/`href` targets before
and after packaging. Only the final distribution folder should be shared, not
the project root, `.build-venv`, `build` or `deployment/toolchain`.

## Acceptance check

Run the automated packaged-GUI check from the project root:

```powershell
.\deployment\test_deployment.ps1
```

It copies the distribution into a new folder, clears developer Python/Tcl paths,
uses an unrelated working directory and launches the EXE directly. An opt-in
runtime hook invokes real Tkinter widgets to check all six season summaries,
graph lines, controls, a full quiz, browser dispatch and Exit. Results are saved
to `deployment/test-results.json`. It opens the report through the real default
browser, but does not verify the browser's visual rendering. The hook is inactive
unless `NOONGAR_DEPLOYMENT_TEST` is set; normal launches use the unchanged app.

Copy the complete distribution to another location, extract it if zipped, and
double-click `NoongarSeasonsExplorer.exe`. No Python command should be needed.

1. Explore all six seasons; verify descriptions, numeric summaries and graph updates.
2. Complete the quiz and check feedback, final score and Close Quiz.
3. Open the full report; check chart images and local downloads in the browser.
4. Check that Quiz, report and Exit controls remain accessible; close with Exit.

The executable is not code-signed. Windows may show a reputation warning for a
newly built executable. Distribution is for Windows x64, not macOS or Linux.

Build logs and the observed acceptance-test result are recorded separately in
this deployment folder. A successful build alone is not proof of a working GUI.
