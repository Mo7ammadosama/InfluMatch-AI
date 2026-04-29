"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  updateMe,
  getMerchantMe,
  getInfluencerMe,
  updateMerchantMe,
  updateInfluencerMe,
  createMerchantProfile,
  createInfluencerProfile,
  getMyStrategistProfile,
  updateStrategistProfile,
  createStrategistProfile,
} from "@/lib/api";
import { toast } from "sonner";
import { Settings, Globe, User, Store, Star, Palette } from "lucide-react";

const CATEGORIES = ["Fashion", "Tech", "Food", "Travel", "Fitness", "Beauty", "Gaming", "Education", "Lifestyle", "Business"];
const PLATFORMS = ["Instagram", "TikTok", "YouTube", "Snapchat", "X (Twitter)"];
const SPECIALIZATIONS = ["Brand Strategy", "Content Planning", "Social Media", "Copywriting", "Video Production", "Influencer Matching", "Campaign Analytics", "Creative Direction"];

function MultiSelect({ options, selected, onChange, label }: {
  options: string[]; selected: string[]; onChange: (v: string[]) => void; label: string;
}) {
  const toggle = (opt: string) =>
    onChange(selected.includes(opt) ? selected.filter((x) => x !== opt) : [...selected, opt]);
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => toggle(opt)}
            className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-all ${
              selected.includes(opt)
                ? "bg-violet-600 border-violet-500 text-white"
                : "border-white/10 text-white/50 hover:border-white/20 hover:text-white/70"
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const { user, lang, setLang } = useApp();
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  // --- User base form ---
  const [userForm, setUserForm] = useState({
    full_name: user?.full_name ?? "",
    full_name_ar: user?.full_name_ar ?? "",
    phone: user?.phone ?? "",
  });

  // --- Merchant form ---
  const [merchantForm, setMerchantForm] = useState({
    business_name: "",
    business_name_ar: "",
    business_category: "",
    website: "",
    city: "Amman",
    description: "",
    description_ar: "",
  });
  const [hasMerchantProfile, setHasMerchantProfile] = useState(false);

  // --- Influencer form ---
  const [influencerForm, setInfluencerForm] = useState({
    display_name: "",
    bio: "",
    bio_ar: "",
    city: "Amman",
    rate_per_post_jod: "",
    rate_per_story_jod: "",
    rate_per_reel_jod: "",
    is_available: true,
    instagram_handle: "",
    instagram_followers: "",
    tiktok_handle: "",
    tiktok_followers: "",
  });
  const [contentCategories, setContentCategories] = useState<string[]>([]);
  const [hasInfluencerProfile, setHasInfluencerProfile] = useState(false);

  // --- CS form ---
  const [csForm, setCsForm] = useState({
    display_name: "",
    display_name_ar: "",
    bio: "",
    bio_ar: "",
    city: "Amman",
    portfolio_url: "",
    consultation_rate_jod: "",
    is_available: true,
  });
  const [csSpecializations, setCsSpecializations] = useState<string[]>([]);
  const [hasCsProfile, setHasCsProfile] = useState(false);

  useEffect(() => {
    const fetches: Promise<unknown>[] = [];

    if (user?.role === "merchant") {
      fetches.push(
        getMerchantMe()
          .then((r) => {
            setHasMerchantProfile(true);
            const d = r.data;
            setMerchantForm({
              business_name: d.business_name ?? "",
              business_name_ar: d.business_name_ar ?? "",
              business_category: d.business_category ?? "",
              website: d.website ?? "",
              city: d.city ?? "Amman",
              description: d.description ?? "",
              description_ar: d.description_ar ?? "",
            });
          })
          .catch(() => setHasMerchantProfile(false))
      );
    }

    if (user?.role === "influencer") {
      fetches.push(
        getInfluencerMe()
          .then((r) => {
            setHasInfluencerProfile(true);
            const d = r.data;
            const sp = d.social_platforms ?? {};
            setInfluencerForm({
              display_name: d.display_name ?? "",
              bio: d.bio ?? "",
              bio_ar: d.bio_ar ?? "",
              city: d.city ?? "Amman",
              rate_per_post_jod: String(d.rate_per_post_jod ?? ""),
              rate_per_story_jod: String(d.rate_per_story_jod ?? ""),
              rate_per_reel_jod: String(d.rate_per_reel_jod ?? ""),
              is_available: d.is_available ?? true,
              instagram_handle: sp.instagram?.handle ?? "",
              instagram_followers: String(sp.instagram?.followers ?? ""),
              tiktok_handle: sp.tiktok?.handle ?? "",
              tiktok_followers: String(sp.tiktok?.followers ?? ""),
            });
            setContentCategories(d.content_categories ?? []);
          })
          .catch(() => setHasInfluencerProfile(false))
      );
    }

    if (user?.role === "creative_strategist") {
      fetches.push(
        getMyStrategistProfile()
          .then((r) => {
            setHasCsProfile(true);
            const d = r.data;
            setCsForm({
              display_name: d.display_name ?? "",
              display_name_ar: d.display_name_ar ?? "",
              bio: d.bio ?? "",
              bio_ar: d.bio_ar ?? "",
              city: d.city ?? "Amman",
              portfolio_url: d.portfolio_url ?? "",
              consultation_rate_jod: String(d.consultation_rate_jod ?? ""),
              is_available: d.is_available ?? true,
            });
            setCsSpecializations(d.specializations ?? []);
          })
          .catch(() => setHasCsProfile(false))
      );
    }

    Promise.all(fetches).finally(() => setLoading(false));
  }, [user?.role]);

  async function saveUser(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await updateMe(userForm);
      toast.success(lang === "ar" ? "تم الحفظ!" : "Profile updated!");
    } catch {
      toast.error(lang === "ar" ? "فشل الحفظ" : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function saveMerchant(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      if (hasMerchantProfile) {
        await updateMerchantMe(merchantForm);
      } else {
        await createMerchantProfile(merchantForm);
        setHasMerchantProfile(true);
      }
      toast.success(lang === "ar" ? "تم حفظ ملف التاجر!" : "Merchant profile saved!");
    } catch {
      toast.error(lang === "ar" ? "فشل الحفظ" : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function saveInfluencer(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const social_platforms: Record<string, object> = {};
      if (influencerForm.instagram_handle) {
        social_platforms.instagram = {
          handle: influencerForm.instagram_handle,
          followers: parseInt(influencerForm.instagram_followers) || 0,
        };
      }
      if (influencerForm.tiktok_handle) {
        social_platforms.tiktok = {
          handle: influencerForm.tiktok_handle,
          followers: parseInt(influencerForm.tiktok_followers) || 0,
        };
      }
      const payload = {
        display_name: influencerForm.display_name,
        bio: influencerForm.bio,
        bio_ar: influencerForm.bio_ar,
        city: influencerForm.city,
        rate_per_post_jod: parseFloat(influencerForm.rate_per_post_jod) || 0,
        rate_per_story_jod: parseFloat(influencerForm.rate_per_story_jod) || 0,
        rate_per_reel_jod: parseFloat(influencerForm.rate_per_reel_jod) || 0,
        is_available: influencerForm.is_available,
        social_platforms,
        content_categories: contentCategories,
      };
      if (hasInfluencerProfile) {
        await updateInfluencerMe(payload);
      } else {
        await createInfluencerProfile(payload);
        setHasInfluencerProfile(true);
      }
      toast.success(lang === "ar" ? "تم الحفظ! جارٍ إعادة احتساب ARIA..." : "Saved! ARIA rescoring...");
    } catch {
      toast.error(lang === "ar" ? "فشل الحفظ" : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function saveCS(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...csForm,
        consultation_rate_jod: parseFloat(csForm.consultation_rate_jod) || 0,
        specializations: csSpecializations,
      };
      if (hasCsProfile) {
        await updateStrategistProfile(payload);
      } else {
        await createStrategistProfile(payload);
        setHasCsProfile(true);
      }
      toast.success(lang === "ar" ? "تم حفظ ملفك الإبداعي!" : "Creative profile saved!");
    } catch {
      toast.error(lang === "ar" ? "فشل الحفظ" : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-3 mb-2">
        <Settings size={22} className="text-white/60" />
        <h1 className="text-2xl font-bold text-white">
          {lang === "ar" ? "الإعدادات" : "Settings"}
        </h1>
      </div>

      {/* ── Account info ── */}
      <div className="aria-card">
        <div className="flex items-center gap-2 mb-4">
          <User size={15} className="text-white/50" />
          <h3 className="font-semibold text-white">{lang === "ar" ? "معلومات الحساب" : "Account Information"}</h3>
        </div>
        <form onSubmit={saveUser} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Email</Label>
              <Input value={user?.email ?? ""} disabled className="opacity-40" />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "رقم الهاتف" : "Phone"}</Label>
              <Input
                value={userForm.phone}
                onChange={(e) => setUserForm((f) => ({ ...f, phone: e.target.value }))}
                placeholder="+962 7x xxx xxxx"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Full Name (EN)</Label>
              <Input
                value={userForm.full_name}
                onChange={(e) => setUserForm((f) => ({ ...f, full_name: e.target.value }))}
                placeholder="Your name"
              />
            </div>
            <div className="space-y-1.5">
              <Label>الاسم الكامل (AR)</Label>
              <Input
                value={userForm.full_name_ar}
                onChange={(e) => setUserForm((f) => ({ ...f, full_name_ar: e.target.value }))}
                placeholder="اسمك"
                dir="rtl"
              />
            </div>
          </div>
          <Button type="submit" disabled={saving} size="sm">
            {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ" : "Save Account")}
          </Button>
        </form>
      </div>

      {/* ── Merchant profile ── */}
      {user?.role === "merchant" && (
        <div className="aria-card">
          <div className="flex items-center gap-2 mb-4">
            <Store size={15} className="text-amber-400" />
            <h3 className="font-semibold text-white">{lang === "ar" ? "ملف التاجر" : "Merchant Profile"}</h3>
            {!hasMerchantProfile && (
              <span className="text-xs text-amber-400/70 bg-amber-400/10 px-2 py-0.5 rounded-full">
                {lang === "ar" ? "غير مكتمل" : "Not set up"}
              </span>
            )}
          </div>
          <form onSubmit={saveMerchant} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Business Name (EN)</Label>
                <Input
                  required
                  value={merchantForm.business_name}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, business_name: e.target.value }))}
                  placeholder="My Business"
                />
              </div>
              <div className="space-y-1.5">
                <Label>اسم العمل (AR)</Label>
                <Input
                  value={merchantForm.business_name_ar}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, business_name_ar: e.target.value }))}
                  placeholder="اسم النشاط"
                  dir="rtl"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "القطاع" : "Category"}</Label>
                <Input
                  required
                  value={merchantForm.business_category}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, business_category: e.target.value }))}
                  placeholder="Fashion, Tech..."
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "المدينة" : "City"}</Label>
                <Input
                  value={merchantForm.city}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, city: e.target.value }))}
                  placeholder="Amman"
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الموقع" : "Website"}</Label>
                <Input
                  value={merchantForm.website}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, website: e.target.value }))}
                  placeholder="https://..."
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Description (EN)</Label>
                <Input
                  value={merchantForm.description}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, description: e.target.value }))}
                  placeholder="About your business"
                />
              </div>
              <div className="space-y-1.5">
                <Label>وصف (AR)</Label>
                <Input
                  value={merchantForm.description_ar}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, description_ar: e.target.value }))}
                  placeholder="نبذة عن نشاطك"
                  dir="rtl"
                />
              </div>
            </div>
            <Button type="submit" variant="merchant" disabled={saving} size="sm">
              {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ ملف التاجر" : "Save Merchant Profile")}
            </Button>
          </form>
        </div>
      )}

      {/* ── Influencer profile ── */}
      {user?.role === "influencer" && (
        <div className="aria-card">
          <div className="flex items-center gap-2 mb-4">
            <Star size={15} className="text-violet-400" />
            <h3 className="font-semibold text-white">{lang === "ar" ? "ملف المؤثر" : "Influencer Profile"}</h3>
            {!hasInfluencerProfile && (
              <span className="text-xs text-violet-400/70 bg-violet-400/10 px-2 py-0.5 rounded-full">
                {lang === "ar" ? "غير مكتمل" : "Not set up"}
              </span>
            )}
          </div>
          <form onSubmit={saveInfluencer} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الاسم المعروض" : "Display Name"}</Label>
                <Input
                  required
                  value={influencerForm.display_name}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, display_name: e.target.value }))}
                  placeholder="@yourname"
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "المدينة" : "City"}</Label>
                <Input
                  value={influencerForm.city}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, city: e.target.value }))}
                  placeholder="Amman"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Bio (EN)</Label>
                <Input
                  value={influencerForm.bio}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, bio: e.target.value }))}
                  placeholder="About you..."
                />
              </div>
              <div className="space-y-1.5">
                <Label>السيرة الذاتية (AR)</Label>
                <Input
                  value={influencerForm.bio_ar}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, bio_ar: e.target.value }))}
                  placeholder="نبذة عنك..."
                  dir="rtl"
                />
              </div>
            </div>

            <div className="border-t border-white/5 pt-3">
              <p className="text-xs text-white/40 mb-3 uppercase tracking-wider">{lang === "ar" ? "حسابات التواصل" : "Social Accounts"}</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>Instagram Handle</Label>
                  <Input
                    value={influencerForm.instagram_handle}
                    onChange={(e) => setInfluencerForm((f) => ({ ...f, instagram_handle: e.target.value }))}
                    placeholder="@handle"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Instagram Followers</Label>
                  <Input
                    type="number"
                    value={influencerForm.instagram_followers}
                    onChange={(e) => setInfluencerForm((f) => ({ ...f, instagram_followers: e.target.value }))}
                    placeholder="10000"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>TikTok Handle</Label>
                  <Input
                    value={influencerForm.tiktok_handle}
                    onChange={(e) => setInfluencerForm((f) => ({ ...f, tiktok_handle: e.target.value }))}
                    placeholder="@handle"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>TikTok Followers</Label>
                  <Input
                    type="number"
                    value={influencerForm.tiktok_followers}
                    onChange={(e) => setInfluencerForm((f) => ({ ...f, tiktok_followers: e.target.value }))}
                    placeholder="5000"
                  />
                </div>
              </div>
            </div>

            <MultiSelect
              label={lang === "ar" ? "تخصصات المحتوى" : "Content Categories"}
              options={CATEGORIES}
              selected={contentCategories}
              onChange={setContentCategories}
            />

            <div className="border-t border-white/5 pt-3">
              <p className="text-xs text-white/40 mb-3 uppercase tracking-wider">{lang === "ar" ? "أسعار الخدمات (JOD)" : "Service Rates (JOD)"}</p>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <Label>Post</Label>
                  <Input type="number" step="0.5" value={influencerForm.rate_per_post_jod} onChange={(e) => setInfluencerForm((f) => ({ ...f, rate_per_post_jod: e.target.value }))} placeholder="25" />
                </div>
                <div className="space-y-1.5">
                  <Label>Story</Label>
                  <Input type="number" step="0.5" value={influencerForm.rate_per_story_jod} onChange={(e) => setInfluencerForm((f) => ({ ...f, rate_per_story_jod: e.target.value }))} placeholder="15" />
                </div>
                <div className="space-y-1.5">
                  <Label>Reel</Label>
                  <Input type="number" step="0.5" value={influencerForm.rate_per_reel_jod} onChange={(e) => setInfluencerForm((f) => ({ ...f, rate_per_reel_jod: e.target.value }))} placeholder="40" />
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="available"
                checked={influencerForm.is_available}
                onChange={(e) => setInfluencerForm((f) => ({ ...f, is_available: e.target.checked }))}
                className="rounded border-white/20 accent-violet-600"
              />
              <label htmlFor="available" className="text-sm text-white/70">
                {lang === "ar" ? "متاح للحجز" : "Available for bookings"}
              </label>
            </div>

            <Button type="submit" disabled={saving} size="sm">
              {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ وإعادة احتساب ARIA" : "Save & Rescore ARIA")}
            </Button>
          </form>
        </div>
      )}

      {/* ── Creative Strategist profile ── */}
      {user?.role === "creative_strategist" && (
        <div className="aria-card">
          <div className="flex items-center gap-2 mb-4">
            <Palette size={15} className="text-emerald-400" />
            <h3 className="font-semibold text-white">{lang === "ar" ? "ملفي الإبداعي" : "Creative Strategist Profile"}</h3>
            {!hasCsProfile && (
              <span className="text-xs text-emerald-400/70 bg-emerald-400/10 px-2 py-0.5 rounded-full">
                {lang === "ar" ? "غير مكتمل" : "Not set up"}
              </span>
            )}
          </div>
          <form onSubmit={saveCS} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الاسم المعروض (EN)" : "Display Name (EN)"}</Label>
                <Input
                  required
                  value={csForm.display_name}
                  onChange={(e) => setCsForm((f) => ({ ...f, display_name: e.target.value }))}
                  placeholder="Creative Ali"
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الاسم (AR)" : "Display Name (AR)"}</Label>
                <Input
                  value={csForm.display_name_ar}
                  onChange={(e) => setCsForm((f) => ({ ...f, display_name_ar: e.target.value }))}
                  placeholder="علي الإبداعي"
                  dir="rtl"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Bio (EN)</Label>
                <Input
                  value={csForm.bio}
                  onChange={(e) => setCsForm((f) => ({ ...f, bio: e.target.value }))}
                  placeholder="Your creative story..."
                />
              </div>
              <div className="space-y-1.5">
                <Label>السيرة (AR)</Label>
                <Input
                  value={csForm.bio_ar}
                  onChange={(e) => setCsForm((f) => ({ ...f, bio_ar: e.target.value }))}
                  placeholder="قصتك الإبداعية..."
                  dir="rtl"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "المدينة" : "City"}</Label>
                <Input
                  value={csForm.city}
                  onChange={(e) => setCsForm((f) => ({ ...f, city: e.target.value }))}
                  placeholder="Amman"
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "سعر الاستشارة (JOD)" : "Rate (JOD/project)"}</Label>
                <Input
                  type="number"
                  step="5"
                  value={csForm.consultation_rate_jod}
                  onChange={(e) => setCsForm((f) => ({ ...f, consultation_rate_jod: e.target.value }))}
                  placeholder="150"
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "رابط الأعمال" : "Portfolio URL"}</Label>
                <Input
                  value={csForm.portfolio_url}
                  onChange={(e) => setCsForm((f) => ({ ...f, portfolio_url: e.target.value }))}
                  placeholder="https://..."
                />
              </div>
            </div>

            <MultiSelect
              label={lang === "ar" ? "التخصصات" : "Specializations"}
              options={SPECIALIZATIONS}
              selected={csSpecializations}
              onChange={setCsSpecializations}
            />

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="cs-available"
                checked={csForm.is_available}
                onChange={(e) => setCsForm((f) => ({ ...f, is_available: e.target.checked }))}
                className="rounded border-white/20 accent-emerald-600"
              />
              <label htmlFor="cs-available" className="text-sm text-white/70">
                {lang === "ar" ? "متاح للمشاريع الجديدة" : "Available for new projects"}
              </label>
            </div>

            <Button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white" disabled={saving} size="sm">
              {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ الملف الإبداعي" : "Save Creative Profile")}
            </Button>
          </form>
        </div>
      )}

      {/* ── Language ── */}
      <div className="aria-card">
        <div className="flex items-center gap-2 mb-3">
          <Globe size={15} className="text-white/50" />
          <h3 className="font-semibold text-white">{lang === "ar" ? "اللغة" : "Language"}</h3>
        </div>
        <div className="flex gap-3">
          {(["en", "ar"] as const).map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all border ${
                lang === l
                  ? "bg-violet-600 border-violet-500 text-white"
                  : "border-white/10 text-white/50 hover:border-white/20"
              }`}
            >
              {l === "en" ? "🇺🇸 English" : "🇯🇴 العربية"}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
