<script setup lang="ts">
import { ListRestart, Settings, Trash2 } from "lucide-vue-next";
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useIdeStore, type Diagnostic } from "../stores/ide";
import AstViewer from "./AstViewer.vue";
import EditorPane from "./EditorPane.vue";
import FileExplorer from "./FileExplorer.vue";
import FileTabs from "./FileTabs.vue";
import OutputTerminal from "./OutputTerminal.vue";
import ProblemsPanel from "./ProblemsPanel.vue";
import SettingsPanel from "./SettingsPanel.vue";
import TokenViewer from "./TokenViewer.vue";
import Toolbar from "./Toolbar.vue";

const ide = useIdeStore();
const route = useRoute();
const settingsOpen = ref(false);

function openDiagnostic(item: Diagnostic) { if (ide.files[item.file]) ide.activeFile = item.file; }
function keydown(event: KeyboardEvent) {
  if (!(event.ctrlKey || event.metaKey)) return;
  if (event.key === "Enter") { event.preventDefault(); ide.run(); }
  else if (event.shiftKey && event.key.toLowerCase() === "f") { event.preventDefault(); ide.format(); }
  else if (event.shiftKey && event.key.toLowerCase() === "b") { event.preventDefault(); ide.check(); }
  else if (event.key.toLowerCase() === "l") { event.preventDefault(); ide.clearOutput(); }
  else if (event.key.toLowerCase() === "s") { event.preventDefault(); ide.output = "Project saved in this browser.\n"; }
  else if (event.key.toLowerCase() === "p") { event.preventDefault(); const name = window.prompt("Open file", ide.activeFile); if (name && ide.files[name]) ide.activeFile = name; }
}
onMounted(() => { window.addEventListener("keydown", keydown); if (typeof route.query.example === "string") ide.loadExample(route.query.example); });
onBeforeUnmount(() => window.removeEventListener("keydown", keydown));
</script>

<template>
  <div class="ide-shell">
    <Toolbar />
    <div class="ide-main">
      <FileExplorer />
      <section class="editor-workspace"><FileTabs /><EditorPane /></section>
    </div>
    <section class="bottom-panel">
      <header><div><button v-for="tab in ['output', 'problems', 'tokens', 'ast']" :key="tab" type="button" :class="{ active: ide.panel === tab }" @click="ide.panel = tab as any">{{ tab }}<span v-if="tab === 'problems' && ide.diagnostics.length">{{ ide.diagnostics.length }}</span></button></div><div><button class="icon-button" type="button" title="Clear output" @click="ide.clearOutput"><Trash2 :size="15" /></button><button class="icon-button" type="button" title="IDE settings" @click="settingsOpen = !settingsOpen"><Settings :size="15" /></button></div></header>
      <OutputTerminal v-if="ide.panel === 'output'" :output="ide.output" />
      <ProblemsPanel v-else-if="ide.panel === 'problems'" :diagnostics="ide.diagnostics" @select="openDiagnostic" />
      <TokenViewer v-else-if="ide.panel === 'tokens'" :tokens="ide.tokens" />
      <AstViewer v-else :ast="ide.ast" />
      <SettingsPanel v-if="settingsOpen" />
    </section>
    <footer class="ide-status"><span>{{ ide.loading ? 'Running' : 'Ready' }}</span><span>{{ ide.activeFile }}</span><span>{{ Object.keys(ide.files).length }} files</span><span>Sova 0.1v restricted</span></footer>
  </div>
</template>
