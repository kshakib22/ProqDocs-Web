import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://kshakib22.github.io",
  base: "/ProqDocs-Web",

  integrations: [
    starlight({
      title: "ProqDocs",
      // Completely deleted the "sidebar" array here!
    }),
  ],
});
