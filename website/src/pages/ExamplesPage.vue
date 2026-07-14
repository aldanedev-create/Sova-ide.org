<script setup lang="ts">
import CodePreview from "../components/CodePreview.vue";
const examples = [
  { id: "hello", title: "Hello and interpolation", output: "Hello Aldane", code: 'let name = "Aldane"\nprint("Hello {name}")' },
  { id: "collections", title: "Collection pipeline", output: "[4, 8]", code: "let values = [1, 2, 3, 4]\nlet result = values.filter(n => n % 2 == 0).map(n => n * 2)\nprint(result)" },
  { id: "classes", title: "Concise class", output: "Health: 75", code: 'class Player(name, health) {\n    function hit(amount) { self.health -= amount }\n}\nlet hero = Player("Aldane", 100)\nhero.hit(25)\nprint("Health: {hero.health}")' },
];
</script>
<template><section class="page-hero compact"><p class="eyebrow">Executable examples</p><h1>Study a pattern, then open it in the IDE.</h1></section><section class="section example-list"><article v-for="example in examples" :key="example.id"><div><h2>{{ example.title }}</h2><p>Expected output: <code>{{ example.output }}</code></p><RouterLink class="button primary" :to="`/ide?example=${example.id}`">Open in IDE</RouterLink></div><CodePreview :code="example.code" :filename="`${example.id}.sova`" /></article></section></template>
