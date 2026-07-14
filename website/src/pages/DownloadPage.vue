<script setup lang="ts">
import { onMounted, ref } from "vue";
import DownloadCard from "../components/DownloadCard.vue";

type Artifact = { filename: string; url: string; sha256: string; size: number; available: boolean };
type Release = {
  version: string;
  released_at: string;
  status: string;
  checksums?: { filename: string; url: string };
  windows: { installer: Artifact; portable: Artifact };
};
const release = ref<Release | null>(null);
onMounted(async () => { release.value = await fetch("/releases/latest.json").then((response) => response.json()); });
</script>

<template>
  <section class="page-hero compact"><p class="eyebrow">Download center</p><h1>Sova for Windows</h1><p>Standalone x64 artifacts bundle the Python-hosted runtime. A separate Python installation is not required.</p></section>
  <section v-if="release" class="section">
    <div class="download-grid">
      <DownloadCard title="Windows x64 installer" v-bind="release.windows.installer" />
      <DownloadCard title="Portable Windows ZIP" v-bind="release.windows.portable" />
    </div>
    <div class="notice">
      <strong>Sova {{ release.version }} - {{ release.released_at }}</strong>
      <p>This first public build is checksummed but not code-signed. Windows SmartScreen may show an unrecognized-publisher warning.</p>
      <a v-if="release.checksums" class="button secondary" :href="release.checksums.url" download>
        Download SHA-256 checksums
      </a>
    </div>
  </section>
  <section class="section band"><h2>System requirements</h2><p>Windows 10 or newer, x64 processor, and approximately 150 MB of available disk space. The portable archive does not change PATH or the registry.</p><RouterLink class="button secondary" to="/install">Installation and troubleshooting</RouterLink></section>
</template>
