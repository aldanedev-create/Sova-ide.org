# Python And NovaDev Bridge

NovaDev is Sova's implementation host and shared-library provider. Trusted `.nova` implementation modules use NovaDev's explicit `allow unsafe_python true` bridge to load Sova engine modules. This is bootstrap code, not Sova user syntax.

Sova source is never sent to Python `eval` or `exec`. It always goes through Sova's lexer, parser, AST, semantic analyzer, and interpreter.

The public online policy disables shell, Python bridges, network access, environment access, local file access, native libraries, and external imports. Local policy can enable capabilities explicitly.

Sova's standard library calls `novadev.standard_library.nova_root()` and aliases those exact objects under `Sova`. This keeps one canonical library registry.
