$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$testRoot = Join-Path $projectRoot ("build/acceptance-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $testRoot | Out-Null
Copy-Item -LiteralPath "$projectRoot/dist/NoongarSeasonsExplorer" -Destination $testRoot -Recurse
$resultPath = Join-Path $testRoot "result.json"
$saved = @{}
foreach ($name in @("TCL_LIBRARY", "TK_LIBRARY", "PYTHONPATH", "PYTHONHOME", "PATH", "NOONGAR_DEPLOYMENT_TEST")) {
    $saved[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}
try {
    # Test the copied executable with no developer Python/Tcl paths and an
    # unrelated working directory. The hook drives real Tkinter callbacks.
    $env:TCL_LIBRARY = $null
    $env:TK_LIBRARY = $null
    $env:PYTHONPATH = $null
    $env:PYTHONHOME = $null
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
    $env:NOONGAR_DEPLOYMENT_TEST = $resultPath
    $process = Start-Process -FilePath "$testRoot/NoongarSeasonsExplorer/NoongarSeasonsExplorer.exe" `
        -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
    if (-not $process.WaitForExit(60000)) {
        Stop-Process -Id $process.Id
        throw "Packaged GUI check timed out. Inspect $testRoot."
    }
    if (-not (Test-Path -LiteralPath $resultPath)) {
        throw "Executable exited without a test result (exit $($process.ExitCode))."
    }
    Copy-Item -LiteralPath $resultPath -Destination "$PSScriptRoot/test-results.json"
    $result = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
    if ($result.status -ne "passed") { throw ($result | ConvertTo-Json -Depth 5) }
    Write-Output ($result | ConvertTo-Json -Depth 5)
} finally {
    foreach ($name in $saved.Keys) {
        [Environment]::SetEnvironmentVariable($name, $saved[$name], "Process")
    }
}
