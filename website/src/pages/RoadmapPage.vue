<script setup lang="ts">
const columns = [
  { title: "Implemented", items: ["Single lexer/parser/AST", "Semantic analysis", "Tree-walking runtime", "Functions and closures", "Classes and inheritance", "Restricted online API"] },
  { title: "In progress", items: ["Editor diagnostics depth", "Formatter stability", "Module package versions", "Code signing"] },
  { title: "Planned", items: ["Sova bytecode", "Stack virtual machine", "Optimization passes", "Async and iterators", "WebAssembly research"] },
  { title: "Experimental", items: ["Traits or interfaces", "Pattern matching", "Native extension boundary", "Optional AOT targets"] },
];
</script>
<template><section class="page-hero compact"><p class="eyebrow">Transparent roadmap</p><h1>Interpreter first. Native options only after stability.</h1><p>Sova 0.1v does not claim C++ performance or advertise planned syntax as implemented.</p></section><section class="section roadmap-grid"><article v-for="column in columns" :key="column.title"><h2>{{ column.title }}</h2><ul><li v-for="item in column.items" :key="item">{{ item }}</li></ul></article></section></template>
