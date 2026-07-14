export function registerCompletions(monaco: any) {
  const words = ["print", "input", "let", "function", "class", "if", "elif", "else", "for", "while", "try", "catch", "import", "export", "Sova.Math", "Sova.Files", "Sova.Json", "Sova.Time", "Sova.Random"];
  monaco.languages.registerCompletionItemProvider("sova", { provideCompletionItems: () => ({ suggestions: words.map((label) => ({ label, kind: monaco.languages.CompletionItemKind.Keyword, insertText: label })) }) });
}
