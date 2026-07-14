# Installation

## Windows installer

Run `SovaSetup-x64-0.1.0.exe`, keep **Add Sova to PATH** selected, and open a new
PowerShell after setup. Verify with `sova version`. Python is bundled and is not
required separately.

The installer can add `.sova` file association, Start Menu and desktop shortcuts,
examples, standard-library source, and offline documentation. Remove Sova from
Windows Settings or the Start Menu uninstaller; uninstall also removes its PATH
entry and association.

## Verify the download

Download `SHA256SUMS.txt` beside the installer or portable ZIP. In PowerShell,
calculate the file hash:

```powershell
(Get-FileHash .\SovaSetup-x64-0.1.0.exe -Algorithm SHA256).Hash.ToLowerInvariant()
Get-Content .\SHA256SUMS.txt
```

The calculated value must exactly match the installer line in the checksum file.
Do not run a download whose hash does not match.

## Portable archive

Extract `SovaPortable-x64-0.1.0.zip`, open PowerShell in `SovaPortable`, and run:

```powershell
.\sova.exe run .\examples\hello.sova
```

The portable archive does not modify PATH or the registry.
