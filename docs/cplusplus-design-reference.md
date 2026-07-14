# C++ Design Reference

The supplied *A Complete Guide to Programming in C++* was used as a language-completeness checklist, not as syntax to copy. Its progression through fundamental types, operators, control flow, functions and defaults, scope and object lifetime, classes and constructors, inheritance and polymorphism, files, and exception handling informed Sova's specification order.

Sova adopts the architectural lessons that a language needs deterministic tokenization, explicit precedence, scoped names, defined construction behavior, method lookup, and structured exceptions. It intentionally chooses different runtime tradeoffs:

- dynamic values with optional annotations instead of required declarations
- automatic memory management instead of pointers and manual allocation
- single inheritance only in 0.1v
- no preprocessor, templates, operator overloading, or manual destructors
- an interpreter now, with bytecode and optional native compilation later

C++ remains a future completeness and performance reference. Sova 0.1v does not claim equivalent speed, memory control, or compile-time guarantees.
