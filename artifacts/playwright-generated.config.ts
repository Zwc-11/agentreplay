import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: "generated-calendar-demo.spec.ts",
  timeout: 10000,
});
