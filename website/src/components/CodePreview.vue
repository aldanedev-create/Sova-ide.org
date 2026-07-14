<script setup lang="ts">
import { Check, Copy } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{ code: string; filename?: string }>();
const copied = ref(false);
async function copy() {
  await navigator.clipboard.writeText(props.code);
  copied.value = true;
  setTimeout(() => (copied.value = false), 1200);
}
</script>

<template>
  <div class="code-preview">
    <div><span>{{ filename || "main.sova" }}</span><button class="icon-button" type="button" :title="copied ? 'Copied' : 'Copy code'" @click="copy"><Check v-if="copied" :size="16" /><Copy v-else :size="16" /></button></div>
    <pre><code>{{ code }}</code></pre>
  </div>
</template>
