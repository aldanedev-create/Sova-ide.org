import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { callApi } from "../services/api";
import { loadProject, resetProject, saveProject } from "../services/localStorage";

export type Diagnostic = { code: string; severity: string; message: string; file: string; line: number; column: number; endLine: number; endColumn: number; suggestion?: string };

export const starterFiles = {
  "main.sova": `let scores = [88, 92, 76, 95]\n\nlet average = scores\n    .filter(score => score >= 80)\n    .average()\n\nprint("Average: {average}")\n`,
  "models/player.sova": `export class Player(name, health) {\n    function isAlive() {\n        return self.health > 0\n    }\n}\n`,
};

const examples: Record<string, string> = {
  hello: `let name = "Aldane"\nprint("Hello {name}")\n`,
  collections: `let values = [1, 2, 3, 4]\nlet result = values.filter(n => n % 2 == 0).map(n => n * 2)\nprint(result)\n`,
  classes: `class Player(name, health) {\n    function hit(amount) { self.health -= amount }\n}\nlet hero = Player("Aldane", 100)\nhero.hit(25)\nprint("Health: {hero.health}")\n`,
};

export const useIdeStore = defineStore("ide", () => {
  const files = ref<Record<string, string>>(loadProject({ ...starterFiles }));
  const activeFile = ref(Object.keys(files.value)[0] || "main.sova");
  const output = ref("Sova 0.1v online runtime ready.\n");
  const diagnostics = ref<Diagnostic[]>([]);
  const tokens = ref<unknown[]>([]);
  const ast = ref<unknown>(null);
  const explanation = ref("");
  const panel = ref<"output" | "problems" | "tokens" | "ast">("output");
  const loading = ref(false);
  const source = computed({ get: () => files.value[activeFile.value] || "", set: (value: string) => { files.value[activeFile.value] = value; } });

  watch(files, (value) => saveProject(value), { deep: true });

  function request() { return { entry: activeFile.value, files: files.value, options: { timeout_ms: 2000, max_steps: 100000 } }; }
  function createFile(name: string) { if (!name.endsWith(".sova")) name += ".sova"; if (!files.value[name]) files.value[name] = "// New Sova module\n"; activeFile.value = name; }
  function renameFile(from: string, to: string) { if (!to.endsWith(".sova")) to += ".sova"; files.value[to] = files.value[from]; delete files.value[from]; activeFile.value = to; }
  function deleteFile(name: string) { if (Object.keys(files.value).length <= 1) return; delete files.value[name]; activeFile.value = Object.keys(files.value)[0]; }
  function clearOutput() { output.value = ""; }
  function reset() { resetProject(); files.value = { ...starterFiles }; activeFile.value = "main.sova"; diagnostics.value = []; output.value = "Project reset.\n"; }
  function loadExample(id: string) { if (examples[id]) { files.value = { "main.sova": examples[id] }; activeFile.value = "main.sova"; } }

  async function run() {
    loading.value = true; panel.value = "output"; output.value = "Running Sova AST...\n";
    try { const data = await callApi<any>("run", request()); diagnostics.value = data.diagnostics || []; output.value = `${data.stdout || ""}${data.stderr ? `\n${data.stderr}` : ""}\n${data.steps ?? 0} steps in ${data.duration_ms ?? 0} ms\n`; }
    catch (error) { output.value = `Request error: ${error instanceof Error ? error.message : error}\n`; }
    finally { loading.value = false; }
  }
  async function check() { loading.value = true; try { const data = await callApi<any>("check", request()); diagnostics.value = data.diagnostics || []; panel.value = "problems"; } finally { loading.value = false; } }
  async function format() { loading.value = true; try { const data = await callApi<any>("format", request()); if (data.source) source.value = data.source; } finally { loading.value = false; } }
  async function inspect(kind: "tokens" | "ast") { loading.value = true; try { const data = await callApi<any>(kind, request()); if (kind === "tokens") tokens.value = data.tokens || []; else ast.value = data.ast; panel.value = kind; } finally { loading.value = false; } }
  async function explain() { loading.value = true; try { const data = await callApi<any>("explain", request()); explanation.value = data.summary || ""; output.value = `${explanation.value}\nPipeline: ${(data.pipeline || []).join(" -> ")}\n`; panel.value = "output"; } finally { loading.value = false; } }

  return { files, activeFile, source, output, diagnostics, tokens, ast, panel, loading, createFile, renameFile, deleteFile, clearOutput, reset, loadExample, run, check, format, inspect, explain };
});
