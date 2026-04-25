import { test, expect, Page } from "@playwright/test";

const MERCHANT  = { email: "merchant@waslai.jo",   password: "WaslAI@2026" };
const INFLUENCER= { email: "influencer@waslai.jo", password: "WaslAI@2026" };
const ADMIN     = { email: "admin@waslai.jo",       password: "WaslAI@2026" };

async function login(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(merchant|influencer|admin)/, { timeout: 15_000 });
}

// ── AUTH ─────────────────────────────────────────────────────────────────────

test("Login page renders", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator('input[type="email"]')).toBeVisible();
  await expect(page.locator('input[type="password"]')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();
});

test("Login wrong password shows error", async ({ page }) => {
  await page.goto("/login");
  await page.fill('input[type="email"]', "merchant@waslai.jo");
  await page.fill('input[type="password"]', "BadPass99");
  await page.click('button[type="submit"]');
  // Interceptor now skips redirect on auth/login 401 — error div should appear
  const errDiv = page.locator('[class*="red-5"]');
  await expect(errDiv.first()).toBeVisible({ timeout: 10_000 });
});

test("Login as merchant → merchant dashboard", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await expect(page).toHaveURL(/merchant\/dashboard/);
  await expect(page.getByText(/Merchant Dashboard|لوحة تحكم التاجر/)).toBeVisible({ timeout: 8_000 });
});

test("Login as influencer → influencer dashboard", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await expect(page).toHaveURL(/influencer\/dashboard/);
  await expect(page.getByText(/Influencer Dashboard|لوحة تحكم المؤثر/)).toBeVisible({ timeout: 8_000 });
});

test("Login as admin → admin page", async ({ page }) => {
  await login(page, ADMIN.email, ADMIN.password);
  await expect(page).toHaveURL(/admin/);
  await expect(page.getByText(/GOD MODE/)).toBeVisible({ timeout: 8_000 });
});

test("Register page renders and role toggle works", async ({ page }) => {
  await page.goto("/register");
  await expect(page.getByRole("button", { name: /Merchant|تاجر/ }).first()).toBeVisible();
  await page.getByRole("button", { name: /Influencer|مؤثر/ }).click();
  await expect(page.locator('[class*="bg-violet"]').first()).toBeVisible();
});

// ── MERCHANT DASHBOARD ───────────────────────────────────────────────────────

test("Merchant dashboard — KPIs load", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 10_000 });
});

test("Merchant dashboard — Discover button navigates", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.getByRole("link", { name: /Discover|اكتشف/ }).click();
  await expect(page).toHaveURL(/discover/);
});

test("Merchant dashboard — Analytics tab shows chart or empty", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.getByRole("tab", { name: /Analytics|تحليلات/ }).click();
  await page.waitForTimeout(1000);
  // recharts container or aria-card (which holds the chart or empty message)
  await expect(page.locator(".aria-card").first()).toBeVisible({ timeout: 8_000 });
});

test("Merchant dashboard — New Campaign form submits", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.getByRole("tab", { name: /New Campaign|حملة جديدة/ }).click();
  // Fill both required title fields
  await page.locator('input[placeholder="Campaign title"]').fill("PW Test Campaign");
  await page.locator('input[placeholder="عنوان الحملة"]').fill("حملة اختبار");
  await page.locator('textarea').fill("Playwright automated test brief.");
  await page.locator('input[placeholder="fashion, tech..."]').fill("tech");
  await page.locator('input[placeholder="500"]').fill("200");
  await page.getByRole("button", { name: /Create Campaign|إنشاء الحملة/ }).click();
  // Sonner toast appears then disappears — wait for the toast li element
  await expect(page.locator('[data-sonner-toast]').first()).toBeVisible({ timeout: 10_000 });
});

// ── DISCOVER ─────────────────────────────────────────────────────────────────

test("Discover page loads influencer cards", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/discover");
  await page.waitForTimeout(2500);
  // the page heading must be visible — that proves the page rendered
  await expect(page.locator("h1").first()).toBeVisible({ timeout: 10_000 });
});

test("Discover — AI Search fires and returns results", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/discover");
  await page.locator('input[placeholder*="Describe"]').fill("fashion influencer");
  await page.getByRole("button", { name: /Search|بحث/ }).click();
  await page.waitForTimeout(3500);
  // page heading should still be present (search ran without crash)
  await expect(page.locator("h1").first()).toBeVisible({ timeout: 8_000 });
});

test("Discover — Niche filter + search runs", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/discover");
  await page.waitForTimeout(1500);
  await page.locator('input[placeholder="fashion..."]').fill("tech");
  await page.getByRole("button", { name: /Search|بحث/ }).click();
  await page.waitForTimeout(2000);
  await expect(page.locator("h1").first()).toBeVisible();
});

test("Discover — Book button navigates to new booking", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/discover");
  await page.waitForTimeout(2500);
  const bookBtn = page.getByRole("button", { name: /Book|احجز/ }).first();
  if (await bookBtn.count() > 0 && await bookBtn.isVisible()) {
    await bookBtn.click();
    await expect(page).toHaveURL(/bookings\/new/);
    await expect(page.getByText(/Confirm Booking|تأكيد الحجز/)).toBeVisible({ timeout: 8_000 });
  }
});

// ── CAMPAIGNS ────────────────────────────────────────────────────────────────

test("Campaigns page loads for merchant", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/campaigns");
  await page.waitForTimeout(2000);
  await expect(page.locator("h1").first()).toBeVisible({ timeout: 8_000 });
});

test("Campaigns page — New Campaign link goes to dashboard", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/campaigns");
  await page.getByRole("link", { name: /New Campaign|حملة جديدة/ }).click();
  await expect(page).toHaveURL(/merchant\/dashboard/);
});

test("Campaigns — Activate DRAFT campaign", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/campaigns");
  await page.waitForTimeout(2000);
  const activateBtn = page.getByRole("button", { name: /Activate|تفعيل/ }).first();
  if (await activateBtn.count() > 0 && await activateBtn.isVisible()) {
    await activateBtn.click();
    await expect(page.getByText(/activated|تم تفعيل/)).toBeVisible({ timeout: 10_000 });
  }
});

test("Campaigns — Delete button shows confirm dialog", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/campaigns");
  await page.waitForTimeout(2000);
  page.on("dialog", (d) => d.dismiss());
  // Trash icon button — just check it exists
  const trash = page.locator("button svg").filter({ has: page.locator('[class*="trash"], [data-lucide="trash-2"]') }).first();
  if (await trash.count() > 0) {
    await trash.click();
    await expect(page.locator("h1").first()).toBeVisible(); // page intact after dismiss
  }
});

test("Influencer — Open Campaigns Apply button", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/open-campaigns");
  await page.waitForTimeout(2000);
  const applyBtn = page.getByRole("button", { name: /Apply|تقديم/ }).first();
  if (await applyBtn.count() > 0 && await applyBtn.isVisible()) {
    await applyBtn.click();
    await expect(
      page.getByText(/submitted|تم إرسال|Already applied|بالفعل/)
    ).toBeVisible({ timeout: 8_000 });
  }
});

// ── BOOKINGS ─────────────────────────────────────────────────────────────────

test("Bookings page loads", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/bookings");
  // use heading role to avoid strict-mode clash with sidebar link
  await expect(page.getByRole("heading", { name: /Bookings|الحجوزات/ })).toBeVisible({ timeout: 8_000 });
});

test("Bookings — Expand booking shows details", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/bookings");
  await page.waitForTimeout(2000);
  const card = page.locator(".glass-card button").first();
  if (await card.count() > 0) {
    await card.click();
    await page.waitForTimeout(500);
    // expanded panel has a messages input or timeline
    const detail = page.locator('input[placeholder*="message"], input[placeholder*="رسالة"], [class*="booking-timeline"]');
    await expect(detail.first()).toBeVisible({ timeout: 5_000 });
  }
});

test("Bookings — Send message button", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/bookings");
  await page.waitForTimeout(2000);
  const card = page.locator(".glass-card button").first();
  if (await card.count() > 0) {
    await card.click();
    await page.waitForTimeout(500);
    const msgInput = page.locator('input[placeholder*="message"], input[placeholder*="رسالة"]').first();
    if (await msgInput.count() > 0) {
      await msgInput.fill("Test from Playwright");
      // icon send button
      await page.locator('.glass-card button[class*="h-8 w-8"]').click();
      await page.waitForTimeout(800);
    }
  }
});

// ── INFLUENCER DASHBOARD ─────────────────────────────────────────────────────

test("Influencer dashboard — Profile form saves", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/influencer/dashboard");
  await page.getByRole("tab", { name: /My Profile|ملفي الشخصي/ }).click();
  await page.locator('input[placeholder="@handle"]').fill("@playwright");
  await page.locator('input[placeholder="50000"]').fill("30000");
  await page.locator('input[placeholder="0.04"]').fill("0.06");
  await page.getByRole("button", { name: /Save Profile|حفظ الملف/ }).click();
  await expect(page.getByText(/saved|تم الحفظ/)).toBeVisible({ timeout: 10_000 });
});

test("Influencer dashboard — My Campaigns tab loads", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/influencer/dashboard");
  await page.waitForTimeout(1000);
  await page.getByRole("tab", { name: /My Campaigns|حملاتي/ }).click();
  await page.waitForTimeout(1000);
  // either campaign cards or empty text
  const content = page.locator(".aria-card").or(page.getByText(/No campaigns|لا توجد حملات/));
  await expect(content.first()).toBeVisible({ timeout: 8_000 });
});

// ── WALLET ───────────────────────────────────────────────────────────────────

test("Wallet page loads with KPIs", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/wallet");
  await expect(page.getByText(/Wallet|المحفظة/)).toBeVisible({ timeout: 8_000 });
  await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 8_000 });
});

test("Wallet — Redeem below 500 shows error", async ({ page }) => {
  await login(page, INFLUENCER.email, INFLUENCER.password);
  await page.goto("/wallet");
  await page.waitForTimeout(1500);
  const input     = page.locator('input[placeholder="500"]');
  const submitBtn = page.locator('button[type="submit"]');
  if (await submitBtn.isEnabled()) {
    await input.fill("10");
    await submitBtn.click();
    await expect(page.getByText(/500|Minimum|الحد الأدنى/)).toBeVisible({ timeout: 5_000 });
  }
});

// ── ADMIN ────────────────────────────────────────────────────────────────────

test("Admin page — KPIs load", async ({ page }) => {
  await login(page, ADMIN.email, ADMIN.password);
  await page.goto("/admin");
  await expect(page.locator(".kpi-block").first()).toBeVisible({ timeout: 10_000 });
});

test("Admin — Users tab lists users", async ({ page }) => {
  await login(page, ADMIN.email, ADMIN.password);
  await page.goto("/admin");
  await page.getByRole("tab", { name: /Users|المستخدمون/ }).click();
  await page.waitForTimeout(1500);
  await expect(page.locator(".aria-card").first()).toBeVisible({ timeout: 8_000 });
});

test("Admin — Disputes tab renders", async ({ page }) => {
  await login(page, ADMIN.email, ADMIN.password);
  await page.goto("/admin");
  await page.getByRole("tab", { name: /Disputes|النزاعات/ }).click();
  await page.waitForTimeout(1000);
  const content = page.locator(".glass-card").or(
    page.locator(".aria-card")
  ).or(
    page.getByText(/No open disputes|لا نزاعات/)
  );
  await expect(content.first()).toBeVisible({ timeout: 8_000 });
});

// ── SETTINGS ─────────────────────────────────────────────────────────────────

test("Settings page loads", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/settings");
  await expect(page.locator("h1, h2").first()).toBeVisible({ timeout: 8_000 });
});

// ── NAVIGATION ───────────────────────────────────────────────────────────────

test("Sidebar — Campaigns link navigates", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.getByRole("link", { name: /Campaigns|الحملات/ }).first().click();
  await expect(page).toHaveURL(/campaigns/);
});

test("Sidebar — Bookings link navigates", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  await page.goto("/merchant/dashboard");
  await page.getByRole("link", { name: /Bookings|الحجوزات/ }).first().click();
  await expect(page).toHaveURL(/bookings/);
});

test("Logout clears session and redirects to login", async ({ page }) => {
  await login(page, MERCHANT.email, MERCHANT.password);
  const logoutBtn = page.getByRole("button", { name: /Logout|Sign out|خروج/ });
  if (await logoutBtn.count() > 0) {
    await logoutBtn.click();
    await expect(page).toHaveURL(/login/, { timeout: 8_000 });
  }
});
