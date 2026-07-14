import JSZip from "jszip";

export async function downloadProject(files: Record<string, string>, name = "my-sova-project") {
  const zip = new JSZip();
  const root = zip.folder(name)!;
  root.file("Sova.toml", `name = "${name}"\nversion = "0.1.0"\nentry = "main.sova"\nsova_version = ">=0.1"\n`);
  Object.entries(files).forEach(([path, source]) => root.file(path, source));
  root.file("README.md", `# ${name}\n\nRun with: sova run main.sova\n`);
  const blob = await zip.generateAsync({ type: "blob" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${name}.zip`;
  link.click();
  URL.revokeObjectURL(link.href);
}
