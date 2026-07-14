# Online IDE

The browser IDE supports multiple `.sova` files, Monaco highlighting, diagnostics,
tokens, AST inspection, formatting, project ZIP downloads, local auto-save, and
keyboard commands. Dotted imports resolve only within the submitted file map.

Run uses the same Sova lexer, parser, AST, semantic analyzer, and interpreter as
the local release under a stricter policy. Online programs have bounded source,
AST, steps, call depth, collections, strings, output, and execution time.

Shell, Python bridges, subprocesses, local files, external imports, native
libraries, unrestricted packages, and network access are disabled online.
