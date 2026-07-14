<script setup lang="ts">
import loader from "@monaco-editor/loader";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useIdeStore } from "../stores/ide";
import { useSettingsStore } from "../stores/settings";
import { registerCompletions } from "../language/completions";
import { markers } from "../language/diagnostics";
import { registerSova } from "../language/sovaLanguage";
import { registerSovaTheme } from "../language/sovaTheme";

const ide = useIdeStore();
const settings = useSettingsStore();
const host = ref<HTMLElement>();
let editor: any;
let monaco: any;
let suppress = false;

onMounted(async () => {
  monaco = await loader.init();
  registerSova(monaco); registerCompletions(monaco); registerSovaTheme(monaco);
  editor = monaco.editor.create(host.value!, { value: ide.source, language: "sova", theme: "sova-dark", automaticLayout: true, minimap: { enabled: false }, fontSize: settings.fontSize, fontFamily: "JetBrains Mono, Consolas, monospace", tabSize: 4, insertSpaces: true, scrollBeyondLastLine: false, wordWrap: "on" });
  editor.onDidChangeModelContent(() => { if (!suppress) ide.source = editor.getValue(); });
});

watch(() => ide.source, (value) => { if (editor && editor.getValue() !== value) { suppress = true; editor.setValue(value); suppress = false; } });
watch(() => ide.activeFile, () => { if (editor) { suppress = true; editor.setValue(ide.source); suppress = false; } });
watch(() => ide.diagnostics, (value) => { if (editor && monaco) monaco.editor.setModelMarkers(editor.getModel(), "sova", markers(monaco, value.filter((item) => item.file === ide.activeFile))); }, { deep: true });
watch(() => settings.fontSize, (value) => editor?.updateOptions({ fontSize: value }));
onBeforeUnmount(() => editor?.dispose());
</script>
<template><div ref="host" class="editor-pane" aria-label="Sova code editor"></div></template>
