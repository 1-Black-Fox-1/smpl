# Rename if you have a different virtual environment directory name
$Venv = "venv"
$ScriptDir = $PSScriptRoot
# Change this if your virtual environment is located elsewhere
$VenvDir = Join-Path $ScriptDir "..\src\$Venv"

$SrcDir   = Join-Path $ScriptDir "..\src"
$BinDir   = Join-Path $ScriptDir "..\bin"
$BuildDir = Join-Path $ScriptDir "..\build"
$SpecDir  = Join-Path $ScriptDir ".."

$VenvWasActivated = $false

if ([string]::IsNullOrEmpty($env:VIRTUAL_ENV)) {
    $ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

    if (-not (Test-Path $ActivateScript)) {
        throw "Virtual environment activation script not found: $ActivateScript"
    }

    & $ActivateScript
    $VenvWasActivated = $true
}

$PyInstallerArgs = @(
    (Join-Path $SrcDir "main.py")
    "--distpath", $BinDir
    "--workpath", $BuildDir
    "--specpath", $SpecDir
    "--name", "smpl"
    "--add-data", "$(Join-Path $SrcDir 'resources\fonts');resources/fonts"
    "--add-data", "$(Join-Path $SrcDir 'resources\images');resources/images"
    "--add-data", "$(Join-Path $SrcDir 'simpleplayer.kv');."
    "--hidden-import", "main"
    "--onefile"
    "--icon=$(Join-Path $SrcDir 'resources\images\simple-player.png')"
    "--noconsole"
)

& pyinstaller @PyInstallerArgs

# if ($LASTEXITCODE -ne 0) {
#     throw "PyInstaller failed with exit code $LASTEXITCODE"
# }

if ($VenvWasActivated -and (Get-Command deactivate -ErrorAction SilentlyContinue)) {
    deactivate
}
