# Variables And Types

Use `let` for every declaration in 0.1v:

```sova
let age = 27
let name: String = "Aldane"
let scores: List<Int> = [88, 92, 76, 95]
let city: String? = null
```

Annotations are optional runtime contracts. Supported names are `Int`, `Float`, `String`, `Bool`, `Null`, `List`, `Tuple`, `Object`, `Function`, and `Any`. Generic arguments are parsed; 0.1v enforces the outer collection kind but does not recursively check every generic item.

Assignment is lexical: a closure can update a variable in an enclosing scope. Re-declaration in the same scope is a semantic error.
