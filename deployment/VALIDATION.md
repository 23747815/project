# Packaged application validation — 5 October 2026

## Result

The Windows x64 executable was built and tested as an executable, not by running
`python app.py`. The final folder is `dist/NoongarSeasonsExplorer/` (about 110 MiB).

Build command used from the project root:

```powershell
.\build_deployment.ps1 -Python .\.build-venv\Scripts\python.exe
```

Automated acceptance command:

```powershell
.\deployment\test_deployment.ps1
```

The acceptance script copied the entire bundle to a separate folder, cleared
Python/Tcl/Tk environment paths, restricted PATH to Windows directories, and
launched the copied EXE with the temporary directory as its working directory.
The bundled test hook ran real Tkinter callbacks inside that executable.

| Check | Observed result |
|---|---|
| Frozen executable | Confirmed `sys.frozen`; executable path recorded in JSON |
| Bundled CSV | Loaded 365 records |
| Six seasons | Birak 62, Bunuru 59, other four seasons 61 records each |
| Weather summary | All four displayed measurements matched the bundled data for each season |
| Temperature graph | Figure updated for every season with two lines and the expected point count |
| Controls | Quiz, report and Exit were mapped and within the main window after every selection |
| Quiz | Four choices, required selection, feedback, answer locking, expected 4/5 result and Close Quiz passed |
| Report button | Correct bundled file URL passed to the real default-browser handler; Windows accepted the request |
| Exit | Main window destroyed and process exited |
| Normal launch | Final EXE also launched without the verification environment variable and displayed the expected window title |
| Runtime assets | All 23 directly required local report/data files exist; all included output files match the originals byte for byte |
| Distribution exclusions | No project raw-data folder, `.git`, `__pycache__`, project tests or analysis/preparation scripts |
| Existing project files | Git diff confirmed no existing tracked files were changed |

Detailed packaged-GUI results are in `test-results.json`; build output is in
`build-log.txt`. The verification hook is inactive during normal launches.

## Issues resolved during building

- PyInstaller was absent. It was installed in a project-local build environment.
- The first dependency download was blocked by restricted network access; the
  permitted download then succeeded.
- Tcl/Tk 9's scripts were embedded in DLL archives rather than available as
  ordinary folders. The build helper now extracts a local copy from those DLLs.
  System Python and application code were not changed.
- Windows PowerShell's handling of redirected native stderr and PyInstaller's
  spec-relative data paths required adjustments to the build script.

## Remaining validation limits

Window capture was unavailable in this execution environment, so this is not a
visual pixel/layout review. The real browser handoff succeeded, but the report's
rendering inside the browser was not visually inspected. This run was on the
development Windows machine with Python paths removed, not a separate clean PC.
Before submitting, perform the short manual check in deployment/README.md on
another Windows x64 computer. The executable is not code-signed.
