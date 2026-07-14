# Sova Platform

Official website, documentation portal, browser IDE, restricted Vercel API, and Windows release tooling for Sova 0.1v.

## Canonical Engine

`../sova/sova_engine/` is the maintained language implementation. `sova_engine/` in this folder is a deployment mirror created by `python scripts/sync_sova.py`; do not edit the mirror directly. The API executes that one AST interpreter and never invokes Python user files, `exec`, a shell, or an alternate parser.

## Local Website

```powershell
cd sova-platform/website
npm install
npm run dev
```

For Python endpoint behavior, run the focused handler tests or use `vercel dev` from `sova-platform/` after installing the Vercel CLI.

## Vercel

Use `sova-platform` as the Vercel project root. Build command and output are defined in `vercel.json`. The Vue app uses history routing and `/api/*` maps to Python functions. Set `SOVA_CORS_ORIGINS` to a comma-separated production allowlist when using a custom domain.

## Security

Online execution validates an in-memory project, normalizes all paths, caps file count/source size/steps/runtime/output/call depth, disables shell, network, local files, environment access, external imports, and native bridges, then discards interpreter state after each request.

## Windows Release

Run `installer/windows/build.ps1` on Windows after installing Python, PyInstaller, and Inno Setup 6. The build script tests the canonical engine, creates standalone executables, assembles the portable ZIP, compiles the Inno installer, and writes SHA-256 checksums under `release/`.

The installer and portable archive also include the declarative editor package
from `../tools/vscode/sova/`. It provides rich highlighting, snippets, language
configuration, and `.sova` icons for VS Code-compatible editors.
