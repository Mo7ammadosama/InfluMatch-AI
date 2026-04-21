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
} from "@/lib/api";
import { toast } from "sonner";
import { Settings, Globe } from "lucide-react";

export default function SettingsPage() {
  const { user, lang, setLang } = useApp();
  const [userForm, setUserForm] = useState({
    full_name_en: user?.full_name_en ?? "",
    full_name_ar: user?.full_name_ar ?? "",
    phone: user?.phone ?? "",
  });
  const [merchantForm, setMerchantForm] = useState({
    business_name_en: "",
    business_name_ar: "",
    industry: "",
    website: "",
    city: "",
  });
  const [influencerForm, setInfluencerForm] = useState({
    instagram_handle: "",
    instagram_followers: "",
    instagram_engagement_rate: "",
    tiktok_handle: "",
    tiktok_followers: "",
    niche: "",
    city: "",
    rate_per_post: "",
    rate_per_story: "",
    rate_per_reel: "",
    is_available: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasMerchantProfile, setHasMerchantProfile] = useState(false);
  const [hasInfluencerProfile, setHasInfluencerProfile] = useState(false);

  useEffect(() => {
    const promises = [];
    if (user?.role === "merchant") {
      promises.push(
        getMerchantMe()
          .then((r) => {
            setHasMerchantProfile(true);
            const d = r.data;
            setMerchantForm({
              business_name_en: d.business_name_en ?? "",
              business_name_ar: d.business_name_ar ?? "",
              industry: d.industry ?? "",
              website: d.website ?? "",
              city: d.city ?? "",
            });
          })
          .catch(() => setHasMerchantProfile(false))
      );
    }
    if (user?.role === "influencer") {
      promises.push(
        getInfluencerMe()
          .then((r) => {
            setHasInfluencerProfile(true);
            const d = r.data;
            setInfluencerForm({
              instagram_handle: d.instagram_handle ?? "",
              instagram_followers: String(d.instagram_followers ?? ""),
              instagram_engagement_rate: String(d.instagram_engagement_rate ?? ""),
              tiktok_handle: d.tiktok_handle ?? "",
              tiktok_followers: String(d.tiktok_followers ?? ""),
              niche: d.niche ?? "",
              city: d.city ?? "",
              rate_per_post: String(d.rate_per_post ?? ""),
              rate_per_story: String(d.rate_per_story ?? ""),
              rate_per_reel: String(d.rate_per_reel ?? ""),
              is_available: d.is_available ?? true,
            });
          })
          .catch(() => setHasInfluencerProfile(false))
      );
    }
    Promise.all(promises).finally(() => setLoading(false));
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
      const payload = {
        ...influencerForm,
        instagram_followers: parseInt(influencerForm.instagram_followers) || 0,
        instagram_engagement_rate: parseFloat(influencerForm.instagram_engagement_rate) || 0,
        tiktok_followers: parseInt(influencerForm.tiktok_followers) || 0,
        rate_per_post: parseFloat(influencerForm.rate_per_post) || 0,
        rate_per_story: parseFloat(influencerForm.rate_per_story) || 0,
        rate_per_reel: parseFloat(influencerForm.rate_per_reel) || 0,
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

      {/* User profile */}
      <div className="aria-card">
        <h3 className="font-semibold text-white mb-4">
          {lang === "ar" ? "معلومات الحساب" : "Account Information"}
        </h3>
        <form onSubmit={saveUser} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Email</Label>
              <Input value={user?.email ?? ""} disabled className="opacity-50" />
            </div>
            <div className="space-y-1.5">
              <Label>Username</Label>
              <Input value={user?.username ?? ""} disabled className="opacity-50" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Full Name (EN)</Label>
              <Input
                value={userForm.full_name_en}
                onChange={(e) => setUserForm((f) => ({ ...f, full_name_en: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>الاسم الكامل (AR)</Label>
              <Input
                value={userForm.full_name_ar}
                onChange={(e) => setUserForm((f) => ({ ...f, full_name_ar: e.target.value }))}
                dir="rtl"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "رقم الهاتف" : "Phone"}</Label>
            <Input
              value={userForm.phone}
              onChange={(e) => setUserForm((f) => ({ ...f, phone: e.target.value }))}
            />
          </div>
          <Button type="submit" disabled={saving}>
            {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ" : "Save")}
          </Button>
        </form>
      </div>

      {/* Merchant profile */}
      {user?.role === "merchant" && (
        <div className="aria-card">
          <h3 className="font-semibold text-white mb-4">
            {lang === "ar" ? "ملف التاجر" : "Merchant Profile"}
          </h3>
          <form onSubmit={saveMerchant} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Business Name (EN)</Label>
                <Input
                  value={merchantForm.business_name_en}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, business_name_en: e.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>اسم العمل (AR)</Label>
                <Input
                  value={merchantForm.business_name_ar}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, business_name_ar: e.target.value }))}
                  dir="rtl"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الصناعة" : "Industry"}</Label>
                <Input
                  value={merchantForm.industry}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, industry: e.target.value }))}
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
                <Label>{lang === "ar" ? "الموقع الإلكتروني" : "Website"}</Label>
                <Input
                  value={merchantForm.website}
                  onChange={(e) => setMerchantForm((f) => ({ ...f, website: e.target.value }))}
                  placeholder="https://..."
                />
              </div>
            </div>
            <Button type="submit" variant="merchant" disabled={saving}>
              {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ الملف" : "Save Profile")}
            </Button>
          </form>
        </div>
      )}

      {/* Influencer profile */}
      {user?.role === "influencer" && (
        <div className="aria-card">
          <h3 className="font-semibold text-white mb-4">
            {lang === "ar" ? "ملف المؤثر" : "Influencer Profile"}
          </h3>
          <form onSubmit={saveInfluencer} className="space-y-4">
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
                <Label>TikTok Handle</Label>
                <Input
                  value={influencerForm.tiktok_handle}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, tiktok_handle: e.target.value }))}
                  placeholder="@handle"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Instagram Followers</Label>
                <Input
                  type="number"
                  value={influencerForm.instagram_followers}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, instagram_followers: e.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Engagement Rate (0-1)</Label>
                <Input
                  type="number"
                  step="0.001"
                  value={influencerForm.instagram_engagement_rate}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, instagram_engagement_rate: e.target.value }))}
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label>Rate/Post (JOD)</Label>
                <Input
                  type="number"
                  value={influencerForm.rate_per_post}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, rate_per_post: e.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Rate/Story (JOD)</Label>
                <Input
                  type="number"
                  value={influencerForm.rate_per_story}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, rate_per_story: e.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Rate/Reel (JOD)</Label>
                <Input
                  type="number"
                  value={influencerForm.rate_per_reel}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, rate_per_reel: e.target.value }))}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Niche</Label>
                <Input
                  value={influencerForm.niche}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, niche: e.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>City</Label>
                <Input
                  value={influencerForm.city}
                  onChange={(e) => setInfluencerForm((f) => ({ ...f, city: e.target.value }))}
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="available"
                checked={influencerForm.is_available}
                onChange={(e) => setInfluencerForm((f) => ({ ...f, is_available: e.target.checked }))}
                className="rounded border-white/20"
              />
              <label htmlFor="available" className="text-sm text-white/70">
                {lang === "ar" ? "متاح للحجز" : "Available for bookings"}
              </label>
            </div>
            <Button type="submit" disabled={saving}>
              {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ وإعادة احتساب ARIA" : "Save & Rescore ARIA")}
            </Button>
          </form>
        </div>
      )}

      {/* Language */}
      <div className="aria-card">
        <div className="flex items-center gap-2 mb-3">
          <Globe size={16} className="text-white/50" />
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
