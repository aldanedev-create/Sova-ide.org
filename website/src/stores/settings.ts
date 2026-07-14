import { defineStore } from "pinia";
import { ref, watch } from "vue";

export const useSettingsStore = defineStore("settings", () => {
  const theme = ref(localStorage.getItem("sova-theme") || "dark");
  const fontSize = ref(Number(localStorage.getItem("sova-font-size") || 14));
  watch(theme, (value) => localStorage.setItem("sova-theme", value));
  watch(fontSize, (value) => localStorage.setItem("sova-font-size", String(value)));
  return { theme, fontSize };
});
