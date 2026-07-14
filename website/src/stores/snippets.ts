import { defineStore } from "pinia";

export const useSnippetsStore = defineStore("snippets", {
  state: () => ({ recent: [] as string[] }),
  actions: { remember(id: string) { this.recent = [id, ...this.recent.filter((item) => item !== id)].slice(0, 10); } },
});
