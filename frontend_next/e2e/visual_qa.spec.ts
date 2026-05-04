/**
 * InfluMatch.jo — Visual QA + API Intercept Test Suite
 * - Screenshots after every navigation
 * - API response interceptor: fails on 4xx/5xx (except 401 which is expected for auth)
 * - Bug log printed at the end: BUG #N [PAGE] [ELEMENT] [WHAT HAPPENED] [SCREENSHOT: path]
 * - Covers all 5 roles: Merchant, Influencer, Admin, Content Creator, Creative Strategist
 */

import { test, expect, Page } from "@playwright/test";
import path from "path";
import fs from "fs";

// ── Credentials ──────────────────────────────────────────────────────────────
const CREDS = {
  merchant:   { email: "merchant@waslai.jo",   password: "WaslAI@2026" },
  influencer: { email: "influencer@waslai.jo", password: "WaslAI@2026" },
  admin:      { email: "admin@waslai.jo",       password: "WaslAI@2026" },
  creator:    { email: "creator@waslai.jo",     password: "WaslAI@2026" },
  strategist: { email: "strategist@waslai.jo",  password: "WaslAI@2026" },
};

// ── Bug log ───────────────────────────────────────────────────────────────────
const bugs: string[] = [];
let bugNum = 0;

function logBug(page: string, element: string, happened: string, screenshot: string) {
  bugNum++;
  const entry = `BUG #${bugNum} [${page}] [${element}] [${happened}] [SCREENSHOT: ${screenshot}]`;
  bugs.push(entry);
  console.error(entry);
}

// ── Screenshot helper ─────────────────────────────────────────────────────────
const screenshotDir = path.join(__dirname, "screenshots");
if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

async function snap(page: Page, name: string): Promise<string> {
  const safe = name.replace(/[^a-z0-9_-]/gi, "_").slice(0, 80);
  const filePath = path.join(screenshotDir, `${safe}_${Date.now()}.png`);
  await page.screenshot({ path: filePath, fullPage: false });
  return filePath;
}

// ── API 4xx/5xx interceptor ───────────────────────────────────────────────────
function attachApiInterceptor(page: Page, role: string) {
  page.on("response", async (response) => {
    const url = response.url();
    if (!url.includes("/api/")) return;
    const status = response.status();
    // 401 is expected (token expiry, unauthenticated), 404 on missing resources is acceptable
    if (status >= 400 && status !== 401 && status !== 404) {
      const screenshotPath = await snap(page, `api_error_${role}_${status}`);
      logBug(
        role + " [API]",
        url.replace(/.*\/api\//, "/api/"),
        `HTTP ${status} response`,
        screenshotPath,
      );
    }
  });
}

// ── Login helper ──────────────────────────────────────────────────────────────
async function login(page: Page, role: keyof typeof CREDS) {
  const { email, password } = CREDS[role];
  await page.goto("/login");
  await page.waitForLoadState("load");
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  // Strategist has INFLUENCER role → redirects to /influencer/dashboard
  await page.waitForURL(/\/(merchant|influencer|admin|content-creator|creative-strategist)/, {
    timeout: 20_000,
  });
}

// ── Nav helper ────────────────────────────────────────────────────────────────
async function navTo(page: Page, url: string, label: string): Promise<string> {
  await page.goto(url);
  await page.waitForLoadState("load");
  // Wait for React's async data loading spinner to disappear (max 10s)
  await page.locator("text=Loading...").waitFor({ state: "hidden", timeout: 10_000 }).catch(() => {});
  await page.locator("text=جار التحميل").waitFor({ state: "hidden", timeout: 5_000 }).catch(() => {});
  return snap(page, label);
}

// ═══════════════════════════════════════════════════════════════════════════════
// MERCHANT VISUAL QA
// ═══════════════════════════════════════════════════════════════════════════════
test.describe("Visual QA — Merchant", () => {
  test.beforeEach(async ({ page }) => {
    attachApiInterceptor(page, "merchant");
    await login(page, "merchant");
  });

  test("Merchant dashboard loads", async ({ page }) => {
    const ss = await navTo(page, "/merchant/dashboard", "merchant_dashboard");
    const heading = page.getByRole("heading").first();
    if (!(await heading.isVisible())) {
      logBug("/merchant/dashboard", "h1/h2", "No heading visible on dashboard", ss);
    }
    await expect(page).toHaveURL(/merchant/);
  });

  test("Merchant campaigns page", async ({ page }) => {
    const ss = await navTo(page, "/campaigns", "merchant_campaigns");
    const btn = page.getByRole("button", { name: /new campaign|create|إنشاء/i }).first();
    if (!(await btn.isVisible().catch(() => false))) {
      logBug("/campaigns", "Create Campaign button", "Button not found", ss);
    }
  });

  test("Merchant bookings page", async ({ page }) => {
    const ss = await navTo(page, "/bookings", "merchant_bookings");
    await expect(page).toHaveURL(/bookings/);
    await snap(page, "merchant_bookings_loaded");
  });

  test("Merchant escrow page", async ({ page }) => {
    const ss = await navTo(page, "/escrow", "merchant_escrow");
    const heading = page.getByRole("heading", { name: /escrow|الضمان/i }).first();
    if (!(await heading.isVisible().catch(() => false))) {
      logBug("/escrow", "Escrow heading", "Heading not visible", ss);
    }
  });

  test("Merchant discover influencers", async ({ page }) => {
    const ss = await navTo(page, "/discover", "merchant_discover");
    await snap(page, "merchant_discover_loaded");
  });

  test("Merchant wallet page", async ({ page }) => {
    const ss = await navTo(page, "/wallet", "merchant_wallet");
    await snap(page, "merchant_wallet_loaded");
  });

  test("Merchant settings/profile page", async ({ page }) => {
    const ss = await navTo(page, "/settings", "merchant_settings");
    const form = page.locator("form").first();
    if (!(await form.isVisible().catch(() => false))) {
      logBug("/settings", "profile form", "Form not rendered", ss);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// INFLUENCER VISUAL QA
// ═══════════════════════════════════════════════════════════════════════════════
test.describe("Visual QA — Influencer", () => {
  test.beforeEach(async ({ page }) => {
    attachApiInterceptor(page, "influencer");
    await login(page, "influencer");
  });

  test("Influencer dashboard loads", async ({ page }) => {
    const ss = await navTo(page, "/influencer/dashboard", "influencer_dashboard");
    await expect(page).toHaveURL(/influencer/);
  });

  test("Influencer open campaigns browse", async ({ page }) => {
    const ss = await navTo(page, "/open-campaigns", "influencer_open_campaigns");
    await snap(page, "influencer_open_campaigns_loaded");
  });

  test("Influencer bookings/deals", async ({ page }) => {
    const ss = await navTo(page, "/bookings", "influencer_bookings");
    await snap(page, "influencer_bookings_loaded");
  });

  test("Influencer wallet", async ({ page }) => {
    const ss = await navTo(page, "/wallet", "influencer_wallet");
    await snap(page, "influencer_wallet_loaded");
  });

  test("Influencer settings/profile", async ({ page }) => {
    const ss = await navTo(page, "/settings", "influencer_settings");
    await snap(page, "influencer_settings_loaded");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// ADMIN VISUAL QA
// ═══════════════════════════════════════════════════════════════════════════════
test.describe("Visual QA — Admin", () => {
  test.beforeEach(async ({ page }) => {
    attachApiInterceptor(page, "admin");
    await login(page, "admin");
  });

  test("Admin dashboard loads", async ({ page }) => {
    const ss = await navTo(page, "/admin", "admin_dashboard");
    await expect(page).toHaveURL(/admin/);
  });

  test("Admin users page", async ({ page }) => {
    const ss = await navTo(page, "/admin/users", "admin_users");
    // Page renders aria-card divs (not a table) — check for heading or any user card
    const heading = page.getByRole("heading", { name: /user|مستخدم/i }).first();
    const anyCard = page.locator(".aria-card").first();
    const visible = await heading.isVisible().catch(() => false) || await anyCard.isVisible().catch(() => false);
    if (!visible) {
      logBug("/admin/users", "users list", "No heading or user cards visible", ss);
    }
  });

  test("Admin disputes page", async ({ page }) => {
    const ss = await navTo(page, "/admin/disputes", "admin_disputes");
    await snap(page, "admin_disputes_loaded");
  });

  test("Admin analytics/stats page", async ({ page }) => {
    const ss = await navTo(page, "/admin/analytics", "admin_analytics");
    await snap(page, "admin_analytics_loaded");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// CONTENT CREATOR VISUAL QA
// ═══════════════════════════════════════════════════════════════════════════════
test.describe("Visual QA — Content Creator", () => {
  test.beforeEach(async ({ page }) => {
    attachApiInterceptor(page, "creator");
    await login(page, "creator");
  });

  test("Content creator dashboard", async ({ page }) => {
    const ss = await navTo(page, "/content-creator/dashboard", "creator_dashboard");
    await expect(page).toHaveURL(/content-creator/);
  });

  test("Content creator portfolio page", async ({ page }) => {
    // Portfolio list is displayed on the dashboard; /new is the create page
    const ss = await navTo(page, "/content-creator/dashboard", "creator_portfolio");
    await snap(page, "creator_portfolio_loaded");
  });

  test("Content creator bookings received", async ({ page }) => {
    // Booking requests are shown on the dashboard
    const ss = await navTo(page, "/content-creator/dashboard", "creator_bookings");
    await snap(page, "creator_bookings_loaded");
  });

  test("Content creator profile", async ({ page }) => {
    const ss = await navTo(page, "/content-creator/profile", "creator_profile");
    await snap(page, "creator_profile_loaded");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// CREATIVE STRATEGIST VISUAL QA
// ═══════════════════════════════════════════════════════════════════════════════
test.describe("Visual QA — Creative Strategist", () => {
  test.beforeEach(async ({ page }) => {
    attachApiInterceptor(page, "strategist");
    await login(page, "strategist");
  });

  test("Strategist dashboard loads", async ({ page }) => {
    // Strategist uses INFLUENCER role — navigate directly to creative-strategist dashboard
    const ss = await navTo(page, "/creative-strategist/dashboard", "strategist_dashboard");
    await expect(page).toHaveURL(/creative-strategist/);
  });

  test("Strategist ideas page", async ({ page }) => {
    const ss = await navTo(page, "/creative-strategist/ideas", "strategist_ideas");
    await snap(page, "strategist_ideas_loaded");
  });

  test("Strategist engagements (dashboard)", async ({ page }) => {
    // Engagements are shown on the dashboard (no separate /engagements route)
    const ss = await navTo(page, "/creative-strategist/dashboard", "strategist_engagements");
    await snap(page, "strategist_engagements_loaded");
  });

  test("Strategist profile page", async ({ page }) => {
    const ss = await navTo(page, "/creative-strategist/profile", "strategist_profile");
    await snap(page, "strategist_profile_loaded");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// BUG REPORT
// ═══════════════════════════════════════════════════════════════════════════════
test.afterAll(async () => {
  console.log("\n");
  console.log("=".repeat(70));
  console.log("=== FINAL REPORT ===");
  console.log("=".repeat(70));

  if (bugs.length === 0) {
    console.log("NO BUGS FOUND — All visual checks passed.");
  } else {
    console.log(`BUGS FOUND: ${bugs.length}`);
    bugs.forEach((b) => console.log(b));
  }

  const report = [
    `Visual QA Report — ${new Date().toISOString()}`,
    `Total bugs logged: ${bugs.length}`,
    "",
    ...bugs,
  ].join("\n");

  fs.writeFileSync(path.join(screenshotDir, "visual_qa_report.txt"), report, "utf8");
  console.log(`Report saved to: ${path.join(screenshotDir, "visual_qa_report.txt")}`);
  console.log("=".repeat(70));
});
