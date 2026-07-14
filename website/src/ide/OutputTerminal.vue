<script setup lang="ts">
import { FitAddon } from "@xterm/addon-fit";
import { Terminal } from "@xterm/xterm";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
const props = defineProps<{ output: string }>();
const host = ref<HTMLElement>();
let terminal: Terminal;
let fit: FitAddon;
onMounted(() => { terminal = new Terminal({ disableStdin: true, convertEol: true, fontFamily: "JetBrains Mono, Consolas, monospace", fontSize: 13, theme: { background: "#0d0f10", foreground: "#e7e9eb", green: "#34d399" } }); fit = new FitAddon(); terminal.loadAddon(fit); terminal.open(host.value!); fit.fit(); terminal.write(props.output); });
watch(() => props.output, (value) => { if (terminal) { terminal.reset(); terminal.write(value); } });
onBeforeUnmount(() => terminal?.dispose());
</script>
<template><div ref="host" class="terminal-host"></div></template>
