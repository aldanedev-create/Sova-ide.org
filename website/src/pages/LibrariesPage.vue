<script setup lang="ts">
const libraries = [
  ["Sova.Math", "Numbers, rounding, roots, powers, and constants."],
  ["Sova.Statistics", "Mean, median, variance, and bounded in-memory analysis."],
  ["Sova.Json", "Encode and decode in-memory values."],
  ["Sova.Time", "Dates, timestamps, and duration helpers."],
  ["Sova.Random", "Random numbers and choices."],
  ["Sova.Regex", "Pattern matching, replacement, and search."],
  ["Sova.Files", "Local-only file reading and writing under explicit policy."],
  ["Sova.VirtualFiles", "Online access to files submitted with the IDE project."],
  ["Sova.Http", "Local-only HTTP access under explicit network policy."],
];
</script>
<template><section class="page-hero compact"><p class="eyebrow">Standard library</p><h1>One canonical implementation, two language namespaces.</h1><p>Sova aliases NovaDev's stable library objects rather than creating duplicate wrappers.</p></section><section class="section"><div class="library-grid"><article v-for="library in libraries" :key="library[0]"><code>{{ library[0] }}</code><p>{{ library[1] }}</p></article></div><div class="notice"><strong>Online restrictions</strong><p>Files, HTTP, email, databases, processes, shell, and native bridges are blocked online. Use VirtualFiles for submitted project data.</p></div></section></template>
