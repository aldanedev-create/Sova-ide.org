# Standard Library

Sova binds NovaDev's canonical library objects under Pascal-cased Sova names:

```txt
Sova.Math        -> Nova.math
Sova.Files       -> Nova.files
Sova.Json        -> Nova.json
Sova.Time        -> Nova.time
Sova.Random      -> Nova.random
Sova.Regex       -> Nova.regex
Sova.Crypto      -> Nova.crypto
Sova.Csv         -> Nova.csv
Sova.Path        -> Nova.path
Sova.Http        -> Nova.http
Sova.Statistics  -> Nova.statistics
```

The aliases point to the same underlying implementation objects. Sova does not define duplicate `SovaMath` or `SovaFiles` classes.

Local policy may permit files, network, email, and databases. Online policy blocks those capabilities and exposes `Sova.VirtualFiles` for submitted in-memory files. Missing optional Python dependencies must raise `LibraryError` with an installation instruction; they must not fail silently.
