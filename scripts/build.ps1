# Rename if you have a different virtual environment directory name
$Venv = "venv"
$ScriptDir = $PSScriptRoot
# Change this if your virtual environment is located elsewhere
$VenvDir = Join-Path $ScriptDir "..\src\$Venv"

$SrcDir   = Join-Path $ScriptDir "..\src"
$BinDir   = Join-Path $ScriptDir "..\bin"
$BuildDir = Join-Path $ScriptDir "..\build"
$SpecFile = Join-Path $ScriptDir "smpl.spec"

$VenvWasActivated = $false

if ([string]::IsNullOrEmpty($env:VIRTUAL_ENV)) {
    $ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

    if (-not (Test-Path $ActivateScript)) {
        throw "Virtual environment activation script not found: $ActivateScript"
    }

    & $ActivateScript
    $VenvWasActivated = $true
}

$PyiMakespecArgs = @(
    (Join-Path $SrcDir "main.py")
    "--specpath", $ScriptDir
    "--name", "smpl"
    "--add-data", "$(Join-Path $SrcDir 'resources\fonts');resources/fonts"
    "--add-data", "$(Join-Path $SrcDir 'resources\images');resources/images"
    "--add-data", "$(Join-Path $SrcDir 'simpleplayer.kv');."
    "--hidden-import", "main"
    "--onefile"
    "--icon=$(Join-Path $SrcDir 'resources\images\simple-player.png')"
    "--noconsole"
)

$PyInstallerArgs = @(
    (Join-Path $ScriptDir "smpl.spec")
    "--distpath", $BinDir
    "--workpath", $BuildDir
    "--clean"
)

& pyi-makespec @PyiMakespecArgs

# if ($LASTEXITCODE -ne 0) {
#    throw "PyInstaller failed with exit code $LASTEXITCODE"
# }

$SpecContent = Get-Content -Path $SpecFile

$NewSpecContent = ""
$i = 0
foreach ($line in $SpecContent) {
    if ($i -eq 1) {
        $NewSpecContent += "`r`nfrom kivy_deps import gstreamer`r`n"
    }
    elseif ($i -eq 23) {
        $NewSpecContent += "    *[Tree(p) for p in (gstreamer.dep_bins)],`r`n"
    }
    else {
    $NewSpecContent += $line + "`r`n"
    }
    $i += 1
}

Set-Content -Path $SpecFile -Value $NewSpecContent

& pyinstaller @PyInstallerArgs

if ($VenvWasActivated -and (Get-Command deactivate -ErrorAction SilentlyContinue)) {
    deactivate
}
