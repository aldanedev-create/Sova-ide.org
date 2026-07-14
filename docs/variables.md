# Variables

Use `let` for every declaration. Reassign a value without repeating `let`.

```sova
let age = 27
age += 1

let name: String = "Aldane"
let scores: List<Int> = [88, 92, 76]
```

Sova is dynamically typed, but annotations document intent and enable basic
runtime checks. `null`, safe access (`user?.address`), and coalescing (`??`) make
missing values explicit. See `variables-and-types.md` for supported annotations.
