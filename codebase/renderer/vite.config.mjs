import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_DEV_SERVER_PORT = 5183;

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "./",
  envDir: path.resolve(__dirname, ".."),
  resolve: { alias: { "@": __dirname } },
  server: { port: DEFAULT_DEV_SERVER_PORT, strictPort: true, host: "127.0.0.1" },
  build: {
    outDir: path.resolve(__dirname, "..", "build-output", "renderer"),
    emptyOutDir: true,
    assetsDir: "assets",
    rolldownOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("@radix-ui/")) return "vendor-radix";
          if (id.includes("lucide-react")) return "vendor-icons";
        },
      },
    },
  },
});
