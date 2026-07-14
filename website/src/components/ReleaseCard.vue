<script setup lang="ts">defineProps<{ version: string; date: string; status: string }>();</script>
<template><article class="release-card"><p class="eyebrow">Latest release</p><h3>Sova {{ version }}</h3><p>{{ date }} - {{ status }}</p><RouterLink class="text-link" to="/releases">Release details</RouterLink></article></template>
