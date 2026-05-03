// astro.config.mjs
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  // 1. Set 'site' to your main GitHub Pages URL
  site: "https://kshakib22.github.io",

  // 2. Set 'base' to your exact repository name (case-sensitive)
  // This makes your homepage live at /ProqDocs-Web/
  base: "/ProqDocs-Web",

  integrations: [
    starlight({
      title: "ProqDocs",
      sidebar: [
        {
          label: "Documentation",
          autogenerate: { directory: "" },
        },
      ],
    }),
  ],
});
