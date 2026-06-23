import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

declare const process: { env: Record<string, string | undefined> };

// VITE_BASE lets the same build serve from "/" (Vercel/Render) or "/agentreplay/" (GitHub Pages).
export default defineConfig({
  base: process.env.VITE_BASE ?? "/",
  plugins: [react()],
  server: { port: 3000 },
  preview: { port: 4173 },
});
