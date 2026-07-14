# Syntax

Blocks use braces and do not require semicolons.

```sova
let name = "Aldane"

if name.length() > 0 {
    print("Hello {name}")
}
```

Comments use `//` or `/* ... */`. Identifiers start with a letter or underscore. Collections use familiar literal forms:

```sova
let list = [1, 2, 3]
let tuple = (1920, 1080)
let object = { name: "Aldane", active: true }
```

Strings interpolate expressions inside braces. Every token records filename, line, column, absolute source offsets, and an end position.
