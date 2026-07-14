# Windows Installer

`build.ps1` syncs canonical sources, runs the focused language tests, freezes the
CLI with PyInstaller, creates a portable ZIP, and compiles the installer with
Inno Setup 6. Its isolated build requirements include PyInstaller and Pillow;
the script installs both from `requirements-build.txt`.

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\windows\build.ps1
```

If freezing finished but a later packaging step was interrupted, resume from the
existing `dist/` executables with `build.ps1 -SkipTests -SkipFreeze`.

The installer registers `.sova`, optionally adds `Sova\bin` to the system PATH,
creates shell and documentation shortcuts, and removes the PATH entry during
uninstall. It can also install Sova highlighting, snippets, and file icons for
VS Code, VSCodium, Cursor, and Windsurf. New terminals see `sova`, `sova-shell`,
`sovafmt`, `sovalint`, and `sova-doc`; an already-open terminal and editor must
be restarted after installation.

Artifacts are written to `release/`. Build on Windows x64 because the generated
executables and Inno Setup package are platform-specific.
