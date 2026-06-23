import { defineConfig } from "@playwright/test";

declare const process: { env: Record<string, string | undefined> };

// The dashboard is offline-first (bundled demo fixture), so the e2e needs only
// the web app — no API/database. Backend behaviour is covered by pytest.
export default defineConfig({
  testDir: "tests/e2e",
  timeout: 60_000,
  expect: { timeout: 20_000 },
  use: { baseURL: "http://localhost:4173" },
  webServer: {
    command: "npm run build -w @agentreplay/web && npm run preview -w @agentreplay/web -- --port 4173 --host",
    url: "http://localhost:4173",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
