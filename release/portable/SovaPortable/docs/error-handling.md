# Error Handling

```sova
try {
    let data = Sova.Files.read("scores.json")
    print(data)
} catch error {
    print("Could not read file: {error}")
}

throw Error("Something failed")

let data = try Sova.Files.read("scores.json") else "{}"
```

Standard diagnostic categories include `Error`, `SyntaxError`, `TypeError`, `NameError`, `IndexError`, `FileError`, `ImportError`, `ValueError`, `RuntimeError`, `LibraryError`, and `ExecutionLimitError`.

Diagnostics include a stable code, filename, line, column, source excerpt, caret, plain-English message, and optional correction. Resource-limit errors cannot be swallowed by ordinary catch/fallback handling.
