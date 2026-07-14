<script setup lang="ts">
import { Boxes, Braces, Gauge, LockKeyhole, PackageOpen, Workflow } from "lucide-vue-next";
import CodePreview from "../components/CodePreview.vue";
import FeatureCard from "../components/FeatureCard.vue";
import HeroSection from "../components/HeroSection.vue";

const comparison = `// Sova\nlet doubled = numbers.map(n => n * 2)\n\n// Python\ndoubled = list(map(lambda n: n * 2, numbers))`;
const features = [
  ["01", "Readable core", "Braces, no required semicolons, interpolation, optional types, and source-located errors."],
  ["02", "Modern collections", "Map, filter, reduce, safe indexing patterns, destructuring, ranges, and object helpers."],
  ["03", "Object-oriented", "Concise classes, constructor shorthand, self, single inheritance, and method overriding."],
  ["04", "Safe capabilities", "Online execution blocks shell, network, local files, native bridges, and path traversal."],
  ["05", "Shared libraries", "Sova aliases NovaDev's canonical Math, Files, Json, Time, Regex, Crypto, and Statistics objects."],
  ["06", "Performance path", "Tree walking today, then bytecode, a stack VM, optimizations, and optional native targets."],
];
</script>

<template>
  <HeroSection />
  <section class="section"><div class="section-heading"><p class="eyebrow">Language design</p><h2>High-level syntax backed by a real pipeline.</h2><p>Sova owns its lexer, parser, AST, semantic analyzer, runtime, CLI, and release lifecycle.</p></div><div class="feature-grid"><FeatureCard v-for="feature in features" :key="feature[0]" :index="feature[0]" :title="feature[1]" :text="feature[2]" /></div></section>
  <section class="section band"><div class="content-split"><div><p class="eyebrow">Less ceremony</p><h2>Common transformations stay close to the problem.</h2><p>First-class lambdas and collection operations remove scaffolding without hiding evaluation order or error locations.</p><RouterLink class="text-link" to="/learn">Follow the learning path</RouterLink></div><CodePreview :code="comparison" filename="comparison.sova" /></div></section>
  <section class="section"><div class="section-heading"><p class="eyebrow">Release 0.1</p><h2>Honest about what is implemented.</h2></div><div class="status-grid"><article><LockKeyhole /><h3>Restricted online runtime</h3><p>AST-only execution with limits and no operating-system escape.</p></article><article><Braces /><h3>One language pipeline</h3><p>No legacy parser, alternate AST, or NovaDev app generator.</p></article><article><Gauge /><h3>Interpreter today</h3><p>Sova does not claim C++ speed; bytecode and native work are roadmap items.</p></article></div></section>
</template>
