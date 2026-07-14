<script setup lang="ts">
import { Download, ShieldCheck } from "lucide-vue-next";
defineProps<{ title: string; filename: string; available: boolean; sha256: string; url: string; size: number }>();

function fileSize(value: number) {
  return `${(value / 1_000_000).toFixed(1)} MB`;
}
</script>
<template><article class="download-card"><Download :size="24" /><h3>{{ title }}</h3><code>{{ filename }}</code><small>{{ fileSize(size) }}</small><p><ShieldCheck :size="15" /> SHA-256: {{ sha256 }}</p><a v-if="available" class="button primary" :href="url" download>Download</a><span v-else class="button disabled">Build pending</span></article></template>
