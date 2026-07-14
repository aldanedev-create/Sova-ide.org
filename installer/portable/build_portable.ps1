param([string]$Version = "0.1.0")
$ErrorActionPreference = "Stop"
$Platform = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Release = Join-Path $Platform "release"
$Staging = Join-Path $Release "staging\Sova"
$PortableRoot = Join-Path $Release "portable\SovaPortable"
$Target = Join-Path $Release "SovaPortable-x64-$Version.zip"
if (Test-Path $PortableRoot) { Remove-Item -LiteralPath $PortableRoot -Recurse -Force }
New-Item -ItemType Directory -Path $PortableRoot -Force | Out-Null
Copy-Item -Path (Join-Path $Staging "bin\*") -Destination $PortableRoot -Force
foreach ($Directory in @("runtime", "stdlib", "examples", "docs", "editor")) {
    Copy-Item -LiteralPath (Join-Path $Staging $Directory) -Destination (Join-Path $PortableRoot $Directory) -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $Staging "LICENSE.txt") -Destination $PortableRoot
Copy-Item -LiteralPath (Join-Path $Staging "README.txt") -Destination $PortableRoot
if (Test-Path $Target) { Remove-Item -LiteralPath $Target -Force }
Compress-Archive -Path $PortableRoot -DestinationPath $Target -CompressionLevel Optimal
Write-Host "Built $Target"
