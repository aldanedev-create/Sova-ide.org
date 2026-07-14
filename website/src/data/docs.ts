import index from "../../../docs/index.md?raw";
import gettingStarted from "../../../docs/getting-started.md?raw";
import installation from "../../../docs/installation.md?raw";
import overview from "../../../docs/language-overview.md?raw";
import syntax from "../../../docs/syntax.md?raw";
import variables from "../../../docs/variables.md?raw";
import variableTypes from "../../../docs/variables-and-types.md?raw";
import operators from "../../../docs/operators.md?raw";
import collections from "../../../docs/collections.md?raw";
import controlFlow from "../../../docs/control-flow.md?raw";
import functions from "../../../docs/functions.md?raw";
import classes from "../../../docs/classes.md?raw";
import modules from "../../../docs/modules.md?raw";
import errorHandling from "../../../docs/error-handling.md?raw";
import standardLibrary from "../../../docs/standard-library.md?raw";
import cli from "../../../docs/cli.md?raw";
import onlineIde from "../../../docs/online-ide.md?raw";
import security from "../../../docs/security.md?raw";
import memoryModel from "../../../docs/memory-model.md?raw";
import performance from "../../../docs/performance-roadmap.md?raw";
import bridge from "../../../docs/python-and-novadev-bridge.md?raw";
import cppReference from "../../../docs/cplusplus-design-reference.md?raw";
import roadmap from "../../../docs/roadmap.md?raw";

export type DocumentationPage = { slug: string; title: string; group: string; body: string };

export const docs: DocumentationPage[] = [
  { slug: "index", title: "Documentation Home", group: "Start", body: index },
  { slug: "getting-started", title: "Getting Started", group: "Start", body: gettingStarted },
  { slug: "installation", title: "Installation", group: "Start", body: installation },
  { slug: "language-overview", title: "Language Overview", group: "Language", body: overview },
  { slug: "syntax", title: "Syntax", group: "Language", body: syntax },
  { slug: "variables", title: "Variables", group: "Language", body: variables },
  { slug: "variables-and-types", title: "Variables and Types", group: "Language", body: variableTypes },
  { slug: "operators", title: "Operators", group: "Language", body: operators },
  { slug: "collections", title: "Collections", group: "Language", body: collections },
  { slug: "control-flow", title: "Control Flow", group: "Language", body: controlFlow },
  { slug: "functions", title: "Functions", group: "Language", body: functions },
  { slug: "classes", title: "Classes", group: "Language", body: classes },
  { slug: "modules", title: "Modules", group: "Projects", body: modules },
  { slug: "error-handling", title: "Error Handling", group: "Language", body: errorHandling },
  { slug: "standard-library", title: "Standard Library", group: "Libraries", body: standardLibrary },
  { slug: "cli", title: "CLI", group: "Tools", body: cli },
  { slug: "online-ide", title: "Online IDE", group: "Tools", body: onlineIde },
  { slug: "security", title: "Security", group: "Runtime", body: security },
  { slug: "memory-model", title: "Memory Model", group: "Runtime", body: memoryModel },
  { slug: "performance-roadmap", title: "Performance Roadmap", group: "Project", body: performance },
  { slug: "python-and-novadev-bridge", title: "NovaDev Bridge", group: "Project", body: bridge },
  { slug: "cplusplus-design-reference", title: "C++ Design Reference", group: "Project", body: cppReference },
  { slug: "roadmap", title: "Language Roadmap", group: "Project", body: roadmap },
];
