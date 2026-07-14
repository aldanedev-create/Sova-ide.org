param(
    [switch]$SkipTests,
    [switch]$SkipFreeze
)
$ErrorActionPreference = "Stop"
$Platform = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Repository = Resolve-Path (Join-Path $Platform "..")
$Version = & (Join-Path $PSScriptRoot "version.ps1")
$Release = Join-Path $Platform "release"
$Build = Join-Path $Platform "build"
$Dist = Join-Path $Platform "dist"
$Staging = Join-Path $Release "staging\Sova"

python (Join-Path $Platform "scripts\sync_sova.py")
python (Join-Path $Platform "scripts\generate_installer_assets.py")
if (-not $SkipTests) {
    python -m unittest discover -s (Join-Path $Repository "sova\tests") -p "test_*.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Sova tests failed." }
}

python -m pip install --disable-pip-version-check -r (Join-Path $PSScriptRoot "requirements-build.txt")
if (Test-Path $Staging) { Remove-Item -LiteralPath $Staging -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $Staging "bin") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Staging "runtime") -Force | Out-Null

if (-not $SkipFreeze) {
    foreach ($Path in @($Build, $Dist)) {
        if (Test-Path $Path) { Remove-Item -LiteralPath $Path -Recurse -Force }
    }
    python -m PyInstaller --clean --noconfirm --workpath $Build --distpath $Dist (Join-Path $PSScriptRoot "sova.spec")
    if ($LASTEXITCODE -ne 0) { throw "Sova CLI freeze failed." }
    python -m PyInstaller --clean --noconfirm --workpath $Build --distpath $Dist (Join-Path $PSScriptRoot "sova_shell.spec")
    if ($LASTEXITCODE -ne 0) { throw "Sova shell freeze failed." }
}
foreach ($Executable in @("sova.exe", "sova-shell.exe")) {
    if (-not (Test-Path (Join-Path $Dist $Executable))) {
        throw "$Executable is missing. Run build.ps1 without -SkipFreeze first."
    }
}
Copy-Item (Join-Path $Dist "sova.exe") (Join-Path $Staging "bin\sova.exe")
Copy-Item (Join-Path $Dist "sova.exe") (Join-Path $Staging "bin\sovafmt.exe")
Copy-Item (Join-Path $Dist "sova.exe") (Join-Path $Staging "bin\sovalint.exe")
Copy-Item (Join-Path $Dist "sova.exe") (Join-Path $Staging "bin\sova-doc.exe")
Copy-Item (Join-Path $Dist "sova-shell.exe") (Join-Path $Staging "bin\sova-shell.exe")
Copy-Item (Join-Path $Platform "docs") (Join-Path $Staging "docs") -Recurse
Copy-Item (Join-Path $Platform "examples") (Join-Path $Staging "examples") -Recurse
Copy-Item (Join-Path $Repository "sova\stdlib") (Join-Path $Staging "stdlib") -Recurse
New-Item -ItemType Directory -Path (Join-Path $Staging "editor\vscode\sova") -Force | Out-Null
Copy-Item (Join-Path $Repository "tools\vscode\sova\*") (Join-Path $Staging "editor\vscode\sova") -Recurse -Force
Copy-Item (Join-Path $PSScriptRoot "runtime\README.txt") (Join-Path $Staging "runtime\README.txt")
Copy-Item (Join-Path $PSScriptRoot "licenses\LICENSE.txt") (Join-Path $Staging "LICENSE.txt")
Copy-Item (Join-Path $Platform "README.md") (Join-Path $Staging "README.txt")

& (Join-Path $Platform "installer\portable\build_portable.ps1") -Version $Version

$IsccCandidates = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$Iscc = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Iscc) { throw "Inno Setup 6 was not found." }
& $Iscc "/DAppVersion=$Version" (Join-Path $PSScriptRoot "installer.iss")
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed." }

$Artifacts = Get-ChildItem $Release -File | Where-Object { $_.Extension -in ".exe", ".zip" }
$Lines = foreach ($Artifact in $Artifacts) {
    $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Artifact.FullName).Hash.ToLowerInvariant()
    "$Hash  $($Artifact.Name)"
}
Set-Content -Path (Join-Path $Release "SHA256SUMS.txt") -Value $Lines -Encoding ascii
Write-Host "Sova $Version release created in $Release"
