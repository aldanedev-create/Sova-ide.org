# CLI

```powershell
sova run app.sova
sova run app.sova --allow-shell
sova shell
sova tokens app.sova
sova ast app.sova
sova check app.sova
sova lint app.sova
sova format app.sova
sova format app.sova --check
sova explain app.sova
sova docs
sova libraries
sova version
sova new my-project
sova test
sova dev app.sova
sova help
```

From a source checkout, replace `sova` with `python sova/sova.py`.

Shell commands are `.load`, `.tokens`, `.ast`, `.env`, `.clear`, `.help`, and `.exit`. Shell environments persist between entries, and expression statements display their result.
