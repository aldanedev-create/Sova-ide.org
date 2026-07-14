# Sova Platform Deployment

The public site and restricted execution API are one Vercel project rooted at
`sova-platform/`. The Vue application is built from `website/`; Python files in
`api/` become serverless functions.

## Local verification

```powershell
python scripts/sync_sova.py
python -m unittest discover -s tests -p "test_*.py" -v
npm --prefix website ci
npm --prefix website run build
npx vercel dev
```

Open the URL printed by Vercel. The IDE sends an in-memory file map to `/api/run`,
`/api/check`, `/api/tokens`, `/api/ast`, `/api/format`, or `/api/explain`.
There is no subprocess in the hosted runner. Shell, Python bridging, networking,
and host file access stay disabled; execution is bounded by source, step, output,
call-depth, collection, and wall-clock limits.

## Vercel production deployment

1. Import the repository in Vercel and set the Root Directory to `sova-platform`.
2. Keep the committed `vercel.json`; do not replace its build or rewrite rules.
3. Set `SOVA_CORS_ORIGINS` to the production origin and any approved preview origins.
4. Deploy, then verify `/api/health`, `/ide`, `/docs`, and one Run action.

The included GitHub workflow can deploy with `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and
`VERCEL_PROJECT_ID` repository secrets.

## Releases

Windows binaries are built on a Windows machine or GitHub Actions, never on
Vercel. A version tag such as `v0.1.0` creates the installer, portable ZIP, and
SHA-256 checksum file. After a local Windows build, run:

```powershell
python scripts/publish_local_release.py
```

The publisher copies both binaries and `SHA256SUMS.txt` into the static download
directory and writes `website/public/releases/latest.json`. Do not mark a binary
available before it has been built and checksummed.
