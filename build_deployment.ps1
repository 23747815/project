param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & $Python deployment/prepare_tk.py
    if ($LASTEXITCODE -ne 0) { throw "Tcl/Tk preparation failed." }
    # An optional local Tcl/Tk repair is used only on the build machine.
    $libraries = Join-Path $PSScriptRoot "deployment/toolchain/libraries"
    if (Test-Path "$libraries/tcl_library/init.tcl") {
        $env:TCL_LIBRARY = "$libraries/tcl_library"
        $env:TK_LIBRARY = "$libraries/tk_library"
    }
    $env:PYINSTALLER_CONFIG_DIR = Join-Path $PSScriptRoot "build/pyinstaller-cache"
    & $Python deployment/check_runtime.py
    if ($LASTEXITCODE -ne 0) { throw "Runtime preflight failed; fix the reported problem before building." }
    # PyInstaller writes normal progress to stderr; Windows PowerShell can
    # otherwise treat redirected progress messages as terminating errors.
    $ErrorActionPreference = "Continue"
    & $Python -m PyInstaller --noconfirm --clean --onedir --windowed `
        --name NoongarSeasonsExplorer --distpath dist --workpath build/pyinstaller `
        --specpath build --add-data "${PSScriptRoot}/outputs/seasons:outputs/seasons" `
        --runtime-hook "${PSScriptRoot}/deployment/verify_packaged_hook.py" `
        --exclude-module pytest --exclude-module IPython --exclude-module notebook app.py
    $buildExit = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    if ($buildExit -ne 0) { throw "PyInstaller build failed." }
    Copy-Item -LiteralPath deployment/USER-README.txt -Destination dist/NoongarSeasonsExplorer/README.txt
    & $Python deployment/check_runtime.py dist/NoongarSeasonsExplorer/_internal
    if ($LASTEXITCODE -ne 0) { throw "Packaged data verification failed." }
    Write-Output "Built dist/NoongarSeasonsExplorer/NoongarSeasonsExplorer.exe"
    Write-Output "Distribute the WHOLE NoongarSeasonsExplorer folder, including _internal."
} finally {
    Pop-Location
}
