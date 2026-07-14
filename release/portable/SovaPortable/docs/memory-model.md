# Memory Model

Sova 0.1v uses automatic memory management supplied by the Python host runtime. Sova programs allocate ordinary values, lists, objects, functions, classes, instances, and modules without explicit deallocation.

There are no pointers, address operators, `malloc`, `free`, manual destructors, or unsafe memory blocks. Closures retain their lexical environments while reachable. Module values remain cached for the life of one interpreter project.

This model is safer and simpler than manual C++ allocation, but it does not provide Rust's compile-time ownership or borrow-checker guarantees. Deterministic resource blocks are a future design topic.
