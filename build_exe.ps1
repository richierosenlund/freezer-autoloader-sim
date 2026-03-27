param(
    [string]$Name = "FreezerAutoloaderSimulator",
    [string]$EntryPoint = "main.py",
    [string]$IconPath = "",
    [switch]$CollectAllPyQt,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

function Resolve-PythonPath {
    $candidates = @(
        (Join-Path $projectRoot "venv\Scripts\python.exe"),
        (Join-Path $projectRoot ".venv\Scripts\python.exe")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "No local virtual environment Python found. Expected venv\\Scripts\\python.exe or .venv\\Scripts\\python.exe"
}

$pythonPath = Resolve-PythonPath

if (-not (Test-Path $EntryPoint)) {
    throw "Entry point not found: $EntryPoint"
}

$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", $Name
)

if ($IconPath -ne "") {
    if (-not (Test-Path $IconPath)) {
        throw "Icon file not found: $IconPath"
    }
    $pyInstallerArgs += @("--icon", $IconPath)
}

if ($CollectAllPyQt) {
    $pyInstallerArgs += @("--collect-all", "PyQt5")
}

$pyInstallerArgs += $EntryPoint

Write-Host "Project root : $projectRoot"
Write-Host "Python path  : $pythonPath"
Write-Host "Build command: $pythonPath $($pyInstallerArgs -join ' ')"

if ($DryRun) {
    Write-Host "Dry run complete. No packages installed, no build executed."
    exit 0
}

# Ensure PyInstaller exists in the selected venv.
$pyInstallerExe = Join-Path (Split-Path -Parent $pythonPath) "pyinstaller.exe"
if (-not (Test-Path $pyInstallerExe)) {
    Write-Host "PyInstaller is not installed in the selected environment."
    Write-Host "Installing PyInstaller into: $pythonPath"
    & $pythonPath -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install PyInstaller"
    }
}

Write-Host "Building single-file executable..."
& $pythonPath @pyInstallerArgs
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed"
}

$exePath = Join-Path $projectRoot "dist\$Name.exe"
if (Test-Path $exePath) {
    Write-Host "Build complete: $exePath"
} else {
    Write-Host "Build finished. Check the dist folder for output."
}
