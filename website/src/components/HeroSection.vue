<script setup lang="ts">
import { ArrowRight, Download } from "lucide-vue-next";
</script>

<template>
  <section class="home-hero">
    <div class="hero-grid" aria-hidden="true"></div>
    <div class="hero-inner">
      <p class="eyebrow">Sova Programming Language 0.1v</p>
      <h1>Sova</h1>
      <p class="tagline">Write less. Express more. Build anything.</p>
      <p class="hero-summary">A readable general-purpose language with modern collections, classes, closures, modules, safe access, and a bounded interpreter designed to grow toward bytecode and native targets.</p>
      <div class="hero-actions">
        <RouterLink class="button primary" to="/ide">Try Sova Online <ArrowRight :size="17" /></RouterLink>
        <RouterLink class="button secondary" to="/download"><Download :size="17" /> Download for Windows</RouterLink>
      </div>
    </div>
    <div class="hero-code" aria-label="Sova code sample">
      <div><span></span><span></span><span></span><b>main.sova</b></div>
      <pre><code>let scores = [88, 92, 76, 95]

let average = scores
    .filter(score => score >= 80)
    .average()

print("Average: {average}")</code></pre>
    </div>
  </section>
</template>
