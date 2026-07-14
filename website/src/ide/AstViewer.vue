<script setup lang="ts">defineProps<{ ast: unknown }>();</script><template><pre class="data-viewer">{{ JSON.stringify(ast, null, 2) }}</pre></template>
