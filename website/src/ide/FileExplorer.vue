<script setup lang="ts">
import { FileCode2, FilePlus2, Pencil, Trash2 } from "lucide-vue-next";
import { useIdeStore } from "../stores/ide";
const ide = useIdeStore();
function create() { const name = window.prompt("New .sova file name", "module.sova"); if (name) ide.createFile(name); }
function rename(name: string) { const value = window.prompt("Rename file", name); if (value && value !== name) ide.renameFile(name, value); }
function remove(name: string) { if (window.confirm(`Delete ${name}?`)) ide.deleteFile(name); }
</script>
<template><aside class="file-explorer"><header><strong>Explorer</strong><button class="icon-button" type="button" title="New Sova file" @click="create"><FilePlus2 :size="16" /></button></header><div class="file-list"><div v-for="(_, name) in ide.files" :key="name" :class="['file-row', { active: name === ide.activeFile }]" @click="ide.activeFile = name"><FileCode2 :size="15" /><span>{{ name }}</span><button type="button" title="Rename file" @click.stop="rename(name)"><Pencil :size="13" /></button><button type="button" title="Delete file" @click.stop="remove(name)"><Trash2 :size="13" /></button></div></div></aside></template>
