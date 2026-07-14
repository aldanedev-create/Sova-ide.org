# Getting Started

Create `hello.sova`:

```sova
let name = "Aldane"
print("Hello {name}")
```

Run it locally with `sova run hello.sova`, or paste it into the online IDE and
press Run. Use `sova check hello.sova` before execution when you only want syntax
and structural diagnostics.

Sova blocks use braces and omit semicolons. Variables use `let`; values are
dynamic unless an optional annotation such as `String` or `List<Int>` is added.
