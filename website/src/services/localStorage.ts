const PROJECT_KEY = "sova-ide-project-v1";

export function loadProject(fallback: Record<string, string>): Record<string, string> {
  try {
    const value = JSON.parse(localStorage.getItem(PROJECT_KEY) || "null");
    return value && typeof value === "object" ? value : fallback;
  } catch {
    return fallback;
  }
}

export function saveProject(files: Record<string, string>) {
  localStorage.setItem(PROJECT_KEY, JSON.stringify(files));
}

export function resetProject() {
  localStorage.removeItem(PROJECT_KEY);
}
