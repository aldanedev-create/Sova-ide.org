export function registerSova(monaco: any) {
  if (!monaco.languages.getLanguages().some((item: any) => item.id === "sova")) monaco.languages.register({ id: "sova", extensions: [".sova"] });
  monaco.languages.setMonarchTokensProvider("sova", {
    keywords: ["let", "function", "return", "if", "elif", "else", "for", "while", "break", "continue", "class", "extends", "import", "from", "as", "export", "try", "catch", "throw", "in", "not", "and", "or", "self", "shell", "is"],
    tokenizer: {
      root: [
        [/\/\*/, "comment", "@comment"], [/\/\/.*$/, "comment"],
        [/"([^"\\]|\\.)*"/, "string"], [/'([^'\\]|\\.)*'/, "string"],
        [/\b(true|false|null)\b/, "constant"], [/\b\d+(\.\d+)?\b/, "number"],
        [/[A-Za-z_][\w]*/, { cases: { "@keywords": "keyword", "@default": "identifier" } }],
        [/[+\-*\/%=!<>?&|.:]+/, "operator"],
      ],
      comment: [[/[^/*]+/, "comment"], [/\*\//, "comment", "@pop"], [/[/*]/, "comment"]],
    },
  });
}
