/**
 * InfluMatch.jo — Full Coverage E2E Test Suite
 * Tests every page, tab, form, and interactive element across all three roles.
 * Runs headless by default; set HEADED=1 env var to override for visual debugging.
 */

import { test, expect, Page } from "@playwright/test";

// ── Credentials ────────────────────────────────────────────────────────────────
const MERCHANT   = { email: "merchant@waslai.jo",   password: "WaslAI@2026" };
const INFLUENCER = { email: "influencer@waslai.jo", password: "WaslAI@2026" };
const ADMIN      = { email: "admin@waslai.jo",      password: "WaslAI@2026" };

// ── Helpers ────────────────────────────────────────────────────────────────────
const consoleErrors: string[] = [];

async function login(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.waitForLoadState("load");
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(merchant|influencer|admin)/, { timeout: 20_000 });
}

function trackErrors(page: Page) {
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(`[${msg.location().url}] ${msg.text()}`);
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Auth", () => {
  test("Login page renders all fields", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("load");
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("Wrong password shows error message", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', MERCHANT.email);
    await page.fill('input[type="password"]', "WrongPass999!");
    await page.click('button[type="submit"]');
    // Error div should appear within 10s (401 returns without redirect)
    const errEl = page.locator('[class*="red"], [class*="error"], [role="alert"]').first();
    await expect(errEl).toBeVisible({ timeout: 10_000 });
  });

  test("Merchant login redirects to /merchant/dashboard", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await expect(page).toHaveURL(/merchant\/dashboard/);
    await expect(page.getByText(/Merchant Dashboard|لوحة تحكم التاجر/)).toBeVisible({ timeout: 10_000 });
  });

  test("Influencer login redirects to /influencer/dashboard", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await expect(page).toHaveURL(/influencer\/dashboard/);
    await expect(page.getByText(/Influencer Dashboard|لوحة تحكم المؤثر/)).toBeVisible({ timeout: 10_000 });
  });

  test("Admin login redirects to /admin and shows GOD MODE", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await expect(page).toHaveURL(/admin/);
    await expect(page.getByText(/GOD MODE/)).toBeVisible({ timeout: 10_000 });
  });

  test("Register page renders and role toggle works", async ({ page }) => {
    await page.goto("/register");
    await page.waitForLoadState("load");
    await expect(page.getByRole("button", { name: /Merchant|تاجر/ }).first()).toBeVisible();
    await page.getByRole("button", { name: /Influencer|مؤثر/ }).first().click();
    // Role toggle should visually select influencer
    await expect(page.locator("h1, h2").first()).toBeVisible();
  });

  test("Logout clears session and redirects to /login", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    const logoutBtn = page.getByRole("button", { name: /Logout|Sign out|خروج/ });
    if (await logoutBtn.count() > 0 && await logoutBtn.isVisible()) {
      await logoutBtn.click();
      await expect(page).toHaveURL(/login/, { timeout: 8_000 });
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// MERCHANT — Dashboard
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Merchant Dashboard", () => {
  test("KPI blocks render with values", async ({ page }) => {
    trackErrors(page);
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.waitForLoadState("load");
    await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 12_000 });
    // All 4 KPI blocks should be present
    expect(await page.locator(".kpi-block").count()).toBeGreaterThanOrEqual(4);
  });

  test("Discover Influencers button navigates to /discover", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.getByRole("link", { name: /Discover Influencers|اكتشف المؤثرين/ }).click();
    await expect(page).toHaveURL(/discover/);
  });

  test("Campaigns tab shows list or empty state", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.waitForLoadState("load");
    // Default tab is Campaigns
    const tab = page.getByRole("tab", { name: /Campaigns|الحملات/ }).first();
    if (await tab.isVisible()) await tab.click();
    await page.waitForTimeout(500);
    const content = page.locator(".aria-card").or(page.getByText(/No campaigns|لا توجد حملات/));
    await expect(content.first()).toBeVisible({ timeout: 8_000 });
  });

  test("Analytics tab renders chart or empty state", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.waitForLoadState("load");
    await page.getByRole("tab", { name: /Analytics|تحليلات/ }).click();
    await page.waitForTimeout(800);
    const content = page.locator(".recharts-wrapper, .aria-card").first();
    await expect(content).toBeVisible({ timeout: 8_000 });
  });

  test("New Campaign tab — form renders all required fields", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.waitForLoadState("load");
    await page.getByRole("tab", { name: /New Campaign|حملة جديدة/ }).click();
    await expect(page.locator('input[placeholder="Campaign title"]')).toBeVisible({ timeout: 6_000 });
    await expect(page.locator('input[placeholder="500"]')).toBeVisible();
    await expect(page.getByRole("button", { name: /Create Campaign|إنشاء الحملة/ })).toBeVisible();
  });

  test("New Campaign form — submits successfully", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.waitForLoadState("load");
    await page.getByRole("tab", { name: /New Campaign|حملة جديدة/ }).click();
    await page.locator('input[placeholder="Campaign title"]').fill("PW Full Coverage Test");
    await page.locator('input[placeholder="عنوان الحملة"]').fill("حملة اختبار شاملة");
    await page.locator('textarea').first().fill("Automated Playwright full coverage test.");
    await page.locator('input[placeholder="fashion, tech..."]').fill("tech");
    await page.locator('input[placeholder="500"]').fill("100");
    await page.getByRole("button", { name: /Create Campaign|إنشاء الحملة/ }).click();
    await expect(page.locator('[data-sonner-toast]').first()).toBeVisible({ timeout: 12_000 });
  });

  test("CC Engagements shortcut card is visible and clickable", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.waitForLoadState("load");
    const ccCard = page.getByText(/Manage CC Engagements|إدارة مشاركات منشئي المحتوى/);
    if (await ccCard.isVisible()) {
      await ccCard.click();
      await expect(page).toHaveURL(/cc-engagements/);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// DISCOVER
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Discover", () => {
  test("Page loads with heading", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });

  test("Influencer cards or empty state render", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover");
    await page.waitForTimeout(2500);
    const content = page.locator(".glass-card, .aria-card, [class*='influencer']").or(
      page.getByText(/No influencers|لا يوجد مؤثرون/)
    );
    await expect(content.first()).toBeVisible({ timeout: 10_000 });
  });

  test("AI Search bar accepts input and fires search", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover");
    await page.waitForLoadState("load");
    const searchInput = page.locator('input[placeholder*="Describe"], input[placeholder*="اوصف"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill("fashion influencer Jordan");
      await page.getByRole("button", { name: /Search|بحث/ }).click();
      await page.waitForTimeout(3500);
      await expect(page.locator("h1").first()).toBeVisible({ timeout: 8_000 });
    }
  });

  test("Niche filter searches results", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover");
    await page.waitForLoadState("load");
    const nicheInput = page.locator('input[placeholder*="fashion"], input[placeholder*="niche"]');
    if (await nicheInput.count() > 0) {
      await nicheInput.fill("tech");
      await page.getByRole("button", { name: /Search|بحث/ }).click();
      await page.waitForTimeout(2000);
      await expect(page.locator("h1").first()).toBeVisible();
    }
  });

  test("Book button navigates to /bookings/new", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover");
    await page.waitForTimeout(2500);
    const bookBtn = page.getByRole("button", { name: /Book Now|احجز الآن/ }).first();
    if (await bookBtn.count() > 0 && await bookBtn.isVisible()) {
      await bookBtn.click();
      await expect(page).toHaveURL(/bookings\/new/, { timeout: 8_000 });
    }
  });

  test("Discover Creators tab loads", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover/creators");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// CAMPAIGNS
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Campaigns", () => {
  test("Campaigns list page loads", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/campaigns");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });

  test("New Campaign link navigates to merchant dashboard", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/campaigns");
    await page.waitForLoadState("load");
    const newBtn = page.getByRole("link", { name: /New Campaign|حملة جديدة/ });
    if (await newBtn.count() > 0) {
      await newBtn.click();
      await expect(page).toHaveURL(/merchant\/dashboard/);
    }
  });

  test("Activate DRAFT campaign if available", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/campaigns");
    await page.waitForTimeout(2000);
    const activateBtn = page.getByRole("button", { name: /Activate|تفعيل/ }).first();
    if (await activateBtn.count() > 0 && await activateBtn.isVisible()) {
      await activateBtn.click();
      await expect(
        page.locator('[data-sonner-toast]').or(page.getByText(/activated|تم تفعيل/))
      ).toBeVisible({ timeout: 10_000 });
    }
  });

  test("Campaign detail page loads", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/campaigns");
    await page.waitForTimeout(2000);
    // Click first campaign link if available
    const campaignLink = page.locator("a[href*='/campaigns/']").first();
    if (await campaignLink.count() > 0) {
      await campaignLink.click();
      await page.waitForLoadState("load");
      await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 8_000 });
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// BOOKINGS
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Bookings", () => {
  test("Merchant bookings page heading renders", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/bookings");
    await page.waitForLoadState("load");
    await expect(
      page.getByRole("heading", { name: /Bookings|الحجوزات/ })
    ).toBeVisible({ timeout: 10_000 });
  });

  test("New booking page renders form", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/bookings/new");
    await page.waitForLoadState("load");
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 8_000 });
  });

  test("Influencer bookings — expand booking shows details", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/bookings");
    await page.waitForTimeout(2000);
    const card = page.locator(".glass-card button").first();
    if (await card.count() > 0 && await card.isVisible()) {
      await card.click();
      await page.waitForTimeout(600);
      const detail = page.locator(
        'input[placeholder*="message"], input[placeholder*="رسالة"], [class*="booking-timeline"]'
      );
      if (await detail.count() > 0) {
        await expect(detail.first()).toBeVisible({ timeout: 5_000 });
      }
    }
  });

  test("Influencer bookings — send message", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/bookings");
    await page.waitForTimeout(2000);
    const card = page.locator(".glass-card button").first();
    if (await card.count() > 0 && await card.isVisible()) {
      await card.click();
      await page.waitForTimeout(600);
      const msgInput = page.locator(
        'input[placeholder*="message"], input[placeholder*="رسالة"]'
      ).first();
      if (await msgInput.count() > 0 && await msgInput.isVisible()) {
        await msgInput.fill("Playwright test message");
        const sendBtn = page.locator('.glass-card button[class*="h-8"]').last();
        if (await sendBtn.count() > 0) await sendBtn.click();
        await page.waitForTimeout(800);
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Contracts", () => {
  test("Contracts page loads with Contract Generator form", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/contracts");
    await page.waitForLoadState("load");
    await expect(page.getByText(/Smart Contracts|العقود الذكية/)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/Contract Generator|مولّد العقود/)).toBeVisible({ timeout: 6_000 });
  });

  test("Contract Generator — form fields render", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/contracts");
    await page.waitForLoadState("load");
    await expect(page.locator('input[placeholder="Business Name"]')).toBeVisible({ timeout: 8_000 });
    await expect(page.locator('input[placeholder="@handle"]')).toBeVisible();
    await expect(page.getByRole("button", { name: /Generate Contract|إنشاء العقد/ })).toBeVisible();
  });

  test("Contract Generator — fills form and submits", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/contracts");
    await page.waitForLoadState("load");
    await page.locator('input[placeholder="Business Name"]').fill("WaslAI Store");
    await page.locator('input[placeholder="@handle"]').fill("@playwright_influencer");
    await page.getByRole("button", { name: /Generate Contract|إنشاء العقد/ }).click();
    // Either a toast or contract text appears
    const result = page.locator('[data-sonner-toast]').or(
      page.getByText(/Generated Contract|العقد المُنشأ/)
    );
    await expect(result.first()).toBeVisible({ timeout: 20_000 });
  });

  test("Policy Q&A — ARIA Ask button submits question", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/contracts");
    await page.waitForLoadState("load");
    await expect(page.getByText(/Ask ARIA|سؤال ARIA/).first()).toBeVisible({ timeout: 8_000 });
    const policyInput = page.locator(
      'input[placeholder*="dispute"], input[placeholder*="نزاع"]'
    );
    if (await policyInput.count() > 0) {
      await policyInput.fill("What is the dispute resolution policy?");
      await page.getByRole("button", { name: /Ask ARIA|سؤال ARIA/ }).click();
      await page.waitForTimeout(6000);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// ESCROW
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Escrow", () => {
  test("Escrow page loads with heading and locked amount", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/escrow");
    await page.waitForLoadState("load");
    await expect(page.getByRole("heading", { name: /Escrow|الضمان المالي/ })).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/Currently locked|المبالغ المحجوزة/)).toBeVisible({ timeout: 6_000 });
  });

  test("Escrow — shows transactions or empty state", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/escrow");
    await page.waitForTimeout(3000);
    const content = page.locator(".glass-card").or(
      page.getByText(/No escrow transactions|لا توجد معاملات/)
    );
    await expect(content.first()).toBeVisible({ timeout: 10_000 });
  });

  test("Influencer escrow /my renders", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/escrow");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });

  test("Escrow — Release Funds button visible for funded transactions", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/escrow");
    await page.waitForTimeout(3000);
    const releaseBtn = page.getByRole("button", { name: /Release Funds|تحرير الأموال/ }).first();
    if (await releaseBtn.count() > 0 && await releaseBtn.isVisible()) {
      // Don't actually click — just confirm it's present and enabled
      await expect(releaseBtn).toBeEnabled();
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// WALLET
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Wallet", () => {
  test("Wallet page loads with My Wallet heading", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/wallet");
    await page.waitForLoadState("load");
    await expect(page.getByText(/My Wallet|المحفظة/)).toBeVisible({ timeout: 10_000 });
  });

  test("Wallet — 3 KPI balance blocks render", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/wallet");
    await page.waitForTimeout(2000);
    await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 10_000 });
    expect(await page.locator(".kpi-block").count()).toBeGreaterThanOrEqual(3);
  });

  test("Wallet — Loyalty Points section renders", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/wallet");
    await page.waitForTimeout(2000);
    await expect(page.getByText(/Loyalty Points|نقاط الولاء/)).toBeVisible({ timeout: 8_000 });
  });

  test("Wallet — Transaction History section renders", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/wallet");
    await page.waitForTimeout(2000);
    const txSection = page.getByText(/Transaction History|سجل المعاملات/);
    await expect(txSection).toBeVisible({ timeout: 8_000 });
  });

  test("Merchant wallet page also loads", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/wallet");
    await page.waitForLoadState("load");
    await expect(page.getByText(/Wallet|المحفظة/)).toBeVisible({ timeout: 10_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// SETTINGS
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Settings", () => {
  test("Settings page loads without crash", async ({ page }) => {
    trackErrors(page);
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/settings");
    await page.waitForLoadState("load");
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 8_000 });
  });

  test("Influencer settings page loads", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/settings");
    await page.waitForLoadState("load");
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 8_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// INFLUENCER — Dashboard
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Influencer Dashboard", () => {
  test("KPI blocks render", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.waitForLoadState("load");
    await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 12_000 });
  });

  test("My Profile tab — form saves", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/influencer/dashboard");
    await page.waitForLoadState("load");
    await page.getByRole("tab", { name: /My Profile|ملفي الشخصي/ }).click();
    await page.locator('input[placeholder="@handle"]').fill("@playwright_test");
    await page.locator('input[placeholder="50000"]').fill("25000");
    await page.locator('input[placeholder="0.04"]').fill("0.05");
    await page.getByRole("button", { name: /Save Profile|حفظ الملف/ }).click();
    await expect(
      page.locator('[data-sonner-toast]').or(page.getByText(/saved|تم الحفظ/)).first()
    ).toBeVisible({ timeout: 12_000 });
  });

  test("My Campaigns tab — loads campaigns or empty", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/influencer/dashboard");
    await page.waitForTimeout(1000);
    await page.getByRole("tab", { name: /My Campaigns|حملاتي/ }).click();
    await page.waitForTimeout(1500);
    const content = page.locator(".aria-card").or(page.getByText(/No campaigns|لا توجد حملات/));
    await expect(content.first()).toBeVisible({ timeout: 8_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// OPEN CAMPAIGNS
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Open Campaigns", () => {
  test("Open campaigns page loads", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/open-campaigns");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });

  test("Apply button submits or shows already-applied", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    await page.goto("/open-campaigns");
    await page.waitForTimeout(2500);
    const applyBtn = page.getByRole("button", { name: /Apply|تقديم/ }).first();
    if (await applyBtn.count() > 0 && await applyBtn.isVisible()) {
      await applyBtn.click();
      await expect(
        page.locator('[data-sonner-toast]').or(
          page.getByText(/submitted|تم إرسال|Already applied|بالفعل/)
        )
      ).toBeVisible({ timeout: 10_000 });
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// ADMIN — Control Center
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Admin — GOD MODE", () => {
  test("GOD MODE heading and subtitle visible", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForLoadState("load");
    await expect(page.getByText(/GOD MODE/)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/ARIA Control Center/)).toBeVisible();
  });

  test("KPI blocks render platform stats", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForTimeout(3000);
    await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 12_000 });
    expect(await page.locator(".kpi-block").count()).toBeGreaterThanOrEqual(5);
  });

  test("Quick nav cards: User Management, Disputes, Analytics", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForLoadState("load");
    await expect(page.getByText(/User Management|إدارة المستخدمين/)).toBeVisible({ timeout: 8_000 });
    await expect(page.getByText(/Disputes|النزاعات/)).toBeVisible();
    await expect(page.getByText(/Analytics|التحليلات/)).toBeVisible();
  });

  test("Run Scoring job button is clickable", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForLoadState("load");
    const scoringBtn = page.getByRole("button", { name: /Run Scoring|تشغيل التقييم/ });
    await expect(scoringBtn).toBeVisible({ timeout: 8_000 });
    await scoringBtn.click();
    await expect(
      page.locator('[data-sonner-toast]').or(page.getByText(/Running|triggered|جار التشغيل/))
    ).toBeVisible({ timeout: 12_000 });
  });

  test("Auto Escrow Release job button exists", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForLoadState("load");
    await expect(
      page.getByRole("button", { name: /Auto Escrow Release|إطلاق الضمان/ })
    ).toBeVisible({ timeout: 8_000 });
  });

  test("Re-Audit Influencers job button exists", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForLoadState("load");
    await expect(
      page.getByRole("button", { name: /Re-Audit|إعادة تدقيق/ })
    ).toBeVisible({ timeout: 8_000 });
  });

  test("RAG Rebuild button is visible", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin");
    await page.waitForLoadState("load");
    await expect(
      page.getByRole("button", { name: /Rebuild RAG|إعادة بناء/ }).or(
        page.getByText(/Rebuild RAG|إعادة بناء/)
      )
    ).toBeVisible({ timeout: 8_000 });
  });
});

test.describe("Admin — Sub-pages", () => {
  test("Admin Users page loads user list", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin/users");
    await page.waitForLoadState("load");
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10_000 });
    await page.waitForTimeout(2000);
    const content = page.locator(".aria-card, .glass-card, table, tr").or(
      page.getByText(/No users|لا يوجد مستخدمون/)
    );
    await expect(content.first()).toBeVisible({ timeout: 10_000 });
  });

  test("Admin Disputes page renders", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin/disputes");
    await page.waitForLoadState("load");
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10_000 });
    const content = page.locator(".glass-card, .aria-card").or(
      page.getByText(/No open disputes|لا نزاعات|Disputes/)
    );
    await expect(content.first()).toBeVisible({ timeout: 10_000 });
  });

  test("Admin Analytics page renders charts or empty", async ({ page }) => {
    await login(page, ADMIN.email, ADMIN.password);
    await page.goto("/admin/analytics");
    await page.waitForLoadState("load");
    await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 10_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// NAVIGATION — Sidebar links
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Sidebar Navigation", () => {
  test("Merchant — Campaigns sidebar link navigates", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.getByRole("link", { name: /Campaigns|الحملات/ }).first().click();
    await expect(page).toHaveURL(/campaigns/);
  });

  test("Merchant — Bookings sidebar link navigates", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/merchant/dashboard");
    await page.getByRole("link", { name: /Bookings|الحجوزات/ }).first().click();
    await expect(page).toHaveURL(/bookings/);
  });

  test("Merchant — Contracts sidebar link navigates", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/merchant/dashboard");
    const contractsLink = page.getByRole("link", { name: /Contracts|العقود/ }).first();
    if (await contractsLink.isVisible()) {
      await contractsLink.click();
      await expect(page).toHaveURL(/contracts/);
    }
  });

  test("Merchant — Wallet sidebar link navigates", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/merchant/dashboard");
    const walletLink = page.getByRole("link", { name: /Wallet|المحفظة/ }).first();
    if (await walletLink.isVisible()) {
      await walletLink.click();
      await expect(page).toHaveURL(/wallet/);
    }
  });

  test("Influencer — Open Campaigns sidebar link navigates", async ({ page }) => {
    await login(page, INFLUENCER.email, INFLUENCER.password);
    const openCampLink = page.getByRole("link", { name: /Open Campaigns|الحملات المفتوحة/ }).first();
    if (await openCampLink.isVisible()) {
      await openCampLink.click();
      await expect(page).toHaveURL(/open-campaigns/);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// CREATIVE STRATEGIST
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Creative Strategist", () => {
  test("Ideas page is publicly browseable by merchant", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/creative-strategist/ideas");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// CONTENT CREATOR
// ═══════════════════════════════════════════════════════════════════════════════

test.describe("Content Creator", () => {
  test("Discover Creators page renders", async ({ page }) => {
    await login(page, MERCHANT.email, MERCHANT.password);
    await page.goto("/discover/creators");
    await page.waitForLoadState("load");
    await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// FINAL — Console error summary
// ═══════════════════════════════════════════════════════════════════════════════

test("No critical console errors during tracked tests", async ({ page }) => {
  // This test just reports accumulated errors from trackErrors() calls above
  if (consoleErrors.length > 0) {
    console.warn("Console errors found during tests:");
    consoleErrors.forEach((e) => console.warn("  ", e));
  }
  // Only fail if there are React/Next render errors (not network 4xx which are expected in tests)
  const renderErrors = consoleErrors.filter(
    (e) =>
      e.includes("Uncaught") ||
      e.includes("TypeError") ||
      e.includes("ReferenceError") ||
      (e.includes("Error:") && !e.includes("404") && !e.includes("401") && !e.includes("Network"))
  );
  expect(renderErrors).toHaveLength(0);
});
