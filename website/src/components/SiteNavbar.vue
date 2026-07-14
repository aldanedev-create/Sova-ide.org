<script setup lang="ts">
import { Menu, X } from "lucide-vue-next";
import { ref } from "vue";

const open = ref(false);
const links = [
  ["Learn", "/learn"],
  ["Docs", "/docs"],
  ["Examples", "/examples"],
  ["Libraries", "/libraries"],
  ["Roadmap", "/roadmap"],
  ["Download", "/download"],
];
</script>

<template>
  <header class="site-nav">
    <RouterLink class="brand" to="/" @click="open = false"><img src="/logo.svg" alt="" /><strong>Sova</strong></RouterLink>
    <button class="icon-button nav-toggle" type="button" :aria-label="open ? 'Close navigation' : 'Open navigation'" :aria-expanded="open" @click="open = !open">
      <X v-if="open" :size="20" /><Menu v-else :size="20" />
    </button>
    <nav :class="{ open }" aria-label="Primary navigation">
      <RouterLink v-for="([label, to]) in links" :key="to" :to="to" @click="open = false">{{ label }}</RouterLink>
    </nav>
    <RouterLink class="button primary nav-ide" to="/ide">Try Sova Online</RouterLink>
  </header>
</template>
