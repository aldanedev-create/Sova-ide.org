<script setup lang="ts">defineProps<{ tokens: unknown[] }>();</script><template><pre class="data-viewer">{{ JSON.stringify(tokens, null, 2) }}</pre></template>
