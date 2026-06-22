import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 60_000,
  use: {
    baseURL: "http://localhost:3000",
  },
  webServer: [
      {
        command: "python -m uvicorn app.main:app --port 8000",
        cwd: "apps/api",
        env: { DEEPSEEK_API_KEY: "" },
        url: "http://127.0.0.1:8000/health",
        reuseExistingServer: true,
        timeout: 30_000,
    },
    {
      command: "npm run dev -w @agentreplay/web",
      url: "http://localhost:3000",
      reuseExistingServer: true,
      timeout: 30_000,
    },
  ],
});
