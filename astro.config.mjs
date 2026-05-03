// astro.config.mjs
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://kshakib22.github.io", // Replace with your actual GitHub username
  base: "/ProqDocs-Web", // Replace with your actual repo name
  integrations: [
    starlight({
      title: "ProqDocs",
      sidebar: [
        {
          label: "Documentation",
          // This line tells Starlight to look at your actual folders/files
          autogenerate: { directory: "" },
        },
      ],
    }),
  ],
});
