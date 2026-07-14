<script setup lang="ts">
import SiteFooter from "../components/SiteFooter.vue";
import SiteNavbar from "../components/SiteNavbar.vue";
</script>

<template>
  <div class="public-shell">
    <SiteNavbar />
    <main><RouterView /></main>
    <SiteFooter />
  </div>
</template>
