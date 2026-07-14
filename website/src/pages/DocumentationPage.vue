<script setup lang="ts">
import MarkdownIt from "markdown-it";
import Prism from "prismjs";
import "prismjs/themes/prism-tomorrow.css";
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import DocsLayout from "../layouts/DocsLayout.vue";
import { docs } from "../data/docs";
import { saveProject } from "../services/localStorage";

const route = useRoute();
const router = useRouter();
const query = ref("");

Prism.languages.sova = {
  comment: [{ pattern: /\/\*[\s\S]*?\*\//, greedy: true }, /\/\/.*$/m],
  string: { pattern: /"(?:\\.|[^"\\])*"/, greedy: true },
  keyword: /\b(?:let|function|return|if|elif|else|for|while|break|continue|class|extends|import|from|as|export|try|catch|throw|in|not|and|or|self|shell|is)\b/,
  boolean: /\b(?:true|false|null)\b/,
  number: /\b\d+(?:\.\d+)?\b/,
  operator: /\?\.|\?\?|=>|->|\*\*|==|!=|>=|<=|\+=|-=|\*=|\/=|\.\.|[+\-*\/%=<>!]/,
  function: /\b[A-Za-z_][A-Za-z0-9_]*(?=\s*\()/,
};

function slug(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9\s-]/g, "").trim().replace(/\s+/g, "-");
}

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  highlight(code, language) {
    const grammar = language === "sova" ? Prism.languages.sova : Prism.languages.plain;
    return Prism.highlight(code, grammar, language || "text");
  },
});
const defaultFence = markdown.renderer.rules.fence!;
markdown.renderer.rules.fence = (tokens, index, options, environment, renderer) =>
  `<div class="docs-code"><div class="docs-code-actions"><button data-code-action="copy" type="button">Copy</button><button data-code-action="run" type="button">Open in IDE</button></div>${defaultFence(tokens, index, options, environment, renderer)}</div>`;
markdown.renderer.rules.heading_open = (tokens, index) => {
  const level = tokens[index].tag;
  const title = tokens[index + 1]?.content || "section";
  return `<${level} id="${slug(title)}">`;
};

const current = computed(() => docs.find((item) => item.slug === route.params.slug) || docs[0]);
const filtered = computed(() => docs.filter((item) => `${item.title} ${item.group} ${item.body}`.toLowerCase().includes(query.value.toLowerCase())));
const rendered = computed(() => markdown.render(current.value.body));
const index = computed(() => docs.findIndex((item) => item.slug === current.value.slug));
const headings = computed(() => [...current.value.body.matchAll(/^##?\s+(.+)$/gm)].map((match) => ({ title: match[1], id: slug(match[1]) })));

function codeAction(event: MouseEvent) {
  const button = (event.target as HTMLElement).closest<HTMLButtonElement>("button[data-code-action]");
  if (!button) return;
  const source = button.closest(".docs-code")?.querySelector("code")?.textContent || "";
  if (button.dataset.codeAction === "copy") {
    navigator.clipboard.writeText(source);
    button.textContent = "Copied";
    window.setTimeout(() => (button.textContent = "Copy"), 1200);
  } else {
    saveProject({ "main.sova": source });
    router.push("/ide");
  }
}
</script>

<template>
  <section class="docs-page">
    <DocsLayout>
      <template #sidebar>
        <RouterLink class="brand docs-brand" to="/"><img src="/logo.svg" alt="" /><strong>Sova Docs</strong></RouterLink>
        <select aria-label="Documentation version"><option>Sova 0.1v</option></select>
        <input v-model="query" class="search-input" aria-label="Search documentation" placeholder="Search docs" />
        <nav><RouterLink v-for="item in filtered" :key="item.slug" :to="`/docs/${item.slug}`"><small>{{ item.group }}</small>{{ item.title }}</RouterLink></nav>
      </template>
      <article class="markdown-body" @click="codeAction" v-html="rendered"></article>
      <div class="docs-pager">
        <RouterLink v-if="index > 0" :to="`/docs/${docs[index - 1].slug}`">Previous: {{ docs[index - 1].title }}</RouterLink>
        <RouterLink v-if="index < docs.length - 1" :to="`/docs/${docs[index + 1].slug}`">Next: {{ docs[index + 1].title }}</RouterLink>
      </div>
      <template #toc><strong>On this page</strong><a v-for="heading in headings" :key="heading.id" :href="`#${heading.id}`">{{ heading.title }}</a></template>
    </DocsLayout>
  </section>
</template>
