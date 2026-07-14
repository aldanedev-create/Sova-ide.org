import { createRouter, createWebHistory } from "vue-router";
import PublicLayout from "../layouts/PublicLayout.vue";

const AboutPage = () => import("../pages/AboutPage.vue");
const DocumentationPage = () => import("../pages/DocumentationPage.vue");
const DownloadPage = () => import("../pages/DownloadPage.vue");
const ExamplesPage = () => import("../pages/ExamplesPage.vue");
const HomePage = () => import("../pages/HomePage.vue");
const IdePage = () => import("../pages/IdePage.vue");
const InstallPage = () => import("../pages/InstallPage.vue");
const LearnPage = () => import("../pages/LearnPage.vue");
const LibrariesPage = () => import("../pages/LibrariesPage.vue");
const ReleasesPage = () => import("../pages/ReleasesPage.vue");
const RoadmapPage = () => import("../pages/RoadmapPage.vue");
const PlaygroundPage = () => import("../pages/PlaygroundPage.vue");

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    {
      path: "/",
      component: PublicLayout,
      children: [
        { path: "", component: HomePage },
        { path: "download", component: DownloadPage },
        { path: "install", component: InstallPage },
        { path: "learn", component: LearnPage },
        { path: "examples", component: ExamplesPage },
        { path: "docs/:slug?", component: DocumentationPage },
        { path: "libraries", component: LibrariesPage },
        { path: "releases", component: ReleasesPage },
        { path: "roadmap", component: RoadmapPage },
        { path: "about", component: AboutPage },
      ],
    },
    { path: "/ide", component: IdePage },
    { path: "/playground", component: PlaygroundPage },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ],
});

router.afterEach((route) => {
  const label = route.path === "/" ? "Sova Programming Language" : `${String(route.name || route.path.split("/").filter(Boolean).pop() || "Sova")} | Sova`;
  document.title = label;
});

export default router;
