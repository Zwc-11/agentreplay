import { test } from "@playwright/test";

// Superseded by dashboard.spec.ts (offline-first UI e2e). Backend run/import
// behaviour is covered by apps/api/tests (pytest). Kept as a no-op to avoid a
// dangling/broken spec.
test.skip("checkout flow (superseded by dashboard.spec.ts)", async () => {});
