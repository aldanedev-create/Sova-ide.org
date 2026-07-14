# Sova Language Support

Official declarative editor support for Sova 0.1v.

## Features

- Rich TextMate highlighting for declarations, classes, imports, types,
  interpolation, Sova libraries, calls, properties, operators, and comments.
- `.sova` file icon and optional **Sova File Icons** theme.
- Bracket matching, comment toggling, folding, automatic closing, and indentation.
- Snippets for variables, functions, classes, control flow, imports, and lambdas.
- No background process, telemetry, or network access.

## Installation

The Sova Windows installer can place this extension in the extension directory
for VS Code, VSCodium, Cursor, or Windsurf. Restart the editor after installation.

For a manual local installation, copy this entire folder to:

```text
%USERPROFILE%\.vscode\extensions\sova.sova-language-0.1.0
```

Then reload VS Code. Run **Preferences: File Icon Theme** and select
**Sova File Icons** if the active icon theme does not recognize `.sova` files.

## Other editors

The grammar at `syntaxes/sova.tmLanguage.json` is standard TextMate JSON. Editors
with TextMate bundle import support can reuse it even when they do not install
VS Code extensions directly.

This package provides highlighting and editing behavior. A language server,
debug adapter, completion engine, and refactoring support are future work.
