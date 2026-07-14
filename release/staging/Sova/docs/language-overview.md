# Sova 0.1v Language Overview

Sova is a dynamically typed, general-purpose language with optional type annotations. It favors readable, semicolon-free statements and brace-delimited blocks. Automatic host memory management is the only memory model exposed to Sova programs.

## Execution Model

Sova 0.1v is a tree-walking interpreter:

```txt
source -> lexer -> tokens -> parser -> AST -> semantic analysis -> interpreter -> output
```

There is one lexer, parser, AST, semantic analyzer, and runtime. Sova does not translate user code to Python and call `exec`. The only Python bridge belongs to the trusted implementation host, not Sova programs.

## Implemented

- integers, floats, strings, booleans, null, lists, tuples, and objects
- optional annotations such as `Int`, `List<Int>`, and `String?`
- assignment and compound assignment
- zero-based and negative indexing, slicing, and destructuring
- conditions, guard returns, loops, ranges, break, and continue
- functions, defaults, named arguments, variadics, lambdas, and closures
- classes, constructor shorthand, `self`, single inheritance, and overriding
- statement exceptions, throw, and fallback try expressions
- local modules, exports, caching, and circular-import detection
- safe property access and null coalescing
- source-located diagnostics and bounded execution

## Not In 0.1v

Pointers, `malloc`, `free`, manual destructors, multiple inheritance, templates, function/operator overloading, access modifiers, a borrow checker, bytecode, and native compilation are not implemented. They are not advertised as current features.
