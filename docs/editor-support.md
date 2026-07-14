# Editor Support

Sova includes a declarative extension for VS Code and compatible editors. It
registers `.sova`, supplies a Sova file icon, and provides rich TextMate scopes
for comments, strings and interpolation, declarations, functions, classes,
types, imports, operators, properties, library namespaces, and function calls.

The Windows installer can install the extension for:

- Visual Studio Code
- VSCodium
- Cursor
- Windsurf

Restart the selected editor after setup. If `.sova` still uses a generic icon,
run **Preferences: File Icon Theme** and select **Sova File Icons**.

The extension also includes snippets and language rules for bracket matching,
comment toggling, folding, auto-closing pairs, and indentation. It does not yet
provide a language server, debugger, semantic completion, or refactoring.

Editors that support importing TextMate grammars can use:

```text
tools/vscode/sova/syntaxes/sova.tmLanguage.json
```
