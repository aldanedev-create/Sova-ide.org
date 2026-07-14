$ErrorActionPreference = "Stop"
$VersionFile = Join-Path $PSScriptRoot "..\..\sova_engine\version.py"
$Match = Select-String -Path $VersionFile -Pattern '__version__\s*=\s*"([^"]+)"'
if (-not $Match) { throw "Could not read the Sova version." }
$Match.Matches[0].Groups[1].Value
