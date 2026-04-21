"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { KpiBlock } from "@/components/kpi-block";
import { AriaScoreRing } from "@/components/aria-score-ring";
import { TierBadge } from "@/components/tier-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  getInfluencerMe,
  getMyCampaigns,
  getWallet,
  createInfluencerProfile,
  updateInfluencerMe,
} from "@/lib/api";
import { InfluencerProfile, Campaign, Wallet } from "@/lib/types";
import { fmtJOD, fmtNum, statusClass } from "@/lib/utils";
import { toast } from "sonner";

export default function InfluencerDashboard() {
  const { user, lang } = useApp();
  const [profile, setProfile] = useState<InfluencerProfile | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [loading, setLoading] = useState(true);
  const [profileForm, setProfileForm] = useState({
    instagram_handle: "",
    instagram_followers: "",
    instagram_engagement_rate: "",
    niche: "",
    city: "",
    rate_per_post: "",
    rate_per_story: "",
    rate_per_reel: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([
      getInfluencerMe().catch(() => null),
      getMyCampaigns().catch(() => null),
      getWallet().catch(() => null),
    ]).then(([p, c, w]) => {
      if (p) setProfile(p.data);
      if (c) setCampaigns(Array.isArray(c.data) ? c.data : (c.data?.data ?? []));
      if (w) setWallet(w.data);
    }).finally(() => setLoading(false));
  }, []);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...profileForm,
        instagram_followers: parseInt(profileForm.instagram_followers) || 0,
        instagram_engagement_rate: parseFloat(profileForm.instagram_engagement_rate) || 0,
        rate_per_post: parseFloat(profileForm.rate_per_post) || 0,
        rate_per_story: parseFloat(profileForm.rate_per_story) || 0,
        rate_per_reel: parseFloat(profileForm.rate_per_reel) || 0,
      };
      if (profile) {
        const r = await updateInfluencerMe(payload);
        setProfile(r.data);
      } else {
        const r = await createInfluencerProfile(payload);
        setProfile(r.data);
      }
      toast.success(lang === "ar" ? "تم الحفظ!" : "Profile saved!");
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

  const name = lang === "ar" ? user?.full_name_ar : user?.full_name_en;
  const score = profile?.aria_score ?? 0;

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Banner */}
      <div className="influencer-banner flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            🌟 {lang === "ar" ? `مرحباً، ${name}` : `Welcome, ${name}`}
          </h1>
          <p className="text-white/50 text-sm mt-1">
            {lang === "ar" ? "لوحة تحكم المؤثر" : "Influencer Dashboard"}
          </p>
        </div>
        {profile && (
          <div className="flex items-center gap-3">
            <TierBadge tier={profile.aria_tier} />
            <AriaScoreRing score={score} size="md" />
          </div>
        )}
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiBlock
          label="ARIA Score"
          value={score}
          accent="violet"
        />
        <KpiBlock
          label={lang === "ar" ? "المستوى" : "Tier"}
          value={profile?.aria_tier ?? "—"}
          accent="amber"
        />
        <KpiBlock
          label={lang === "ar" ? "الأرباح (JOD)" : "Earnings (JOD)"}
          value={fmtJOD((wallet as Record<string,number>|null)?.jod_value ?? ((wallet?.available_points ?? 0) * 0.001))}
          accent="green"
        />
        <KpiBlock
          label={lang === "ar" ? "الحملات النشطة" : "Active Campaigns"}
          value={campaigns.filter((c) => c.status === "ACTIVE" || c.status === "IN_PROGRESS").length}
          accent="blue"
        />
      </div>

      {/* Setup prompt if no profile */}
      {!profile && (
        <div className="aria-card border border-amber-500/20 bg-amber-500/5">
          <h3 className="font-semibold text-amber-400 mb-1">
            {lang === "ar" ? "أكمل ملفك الشخصي" : "Complete Your Profile"}
          </h3>
          <p className="text-white/50 text-sm">
            {lang === "ar"
              ? "أضف بياناتك للحصول على نقاط ARIA والظهور في نتائج البحث."
              : "Add your details to get your ARIA score and appear in search results."}
          </p>
        </div>
      )}

      <Tabs defaultValue={profile ? "campaigns" : "profile"}>
        <TabsList>
          <TabsTrigger value="campaigns">{lang === "ar" ? "حملاتي" : "My Campaigns"}</TabsTrigger>
          <TabsTrigger value="profile">{lang === "ar" ? "ملفي الشخصي" : "My Profile"}</TabsTrigger>
        </TabsList>

        {/* Campaigns */}
        <TabsContent value="campaigns">
          <div className="space-y-3">
            {campaigns.map((c) => (
              <div key={c.id} className="aria-card flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white text-sm truncate">
                    {lang === "ar" ? c.title_ar : c.title_en}
                  </div>
                  <div className="text-white/40 text-xs mt-0.5">{c.niche} • {c.end_date}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-violet-400 text-sm">{fmtJOD(c.budget_per_influencer ?? 0)}</span>
                  <span className={statusClass(c.status)}>{c.status}</span>
                </div>
              </div>
            ))}
            {campaigns.length === 0 && (
              <div className="text-white/30 text-sm text-center py-8">
                {lang === "ar" ? "لا توجد حملات بعد." : "No campaigns yet."}
              </div>
            )}
          </div>
        </TabsContent>

        {/* Profile form */}
        <TabsContent value="profile">
          <div className="aria-card max-w-2xl">
            <h3 className="font-semibold text-white mb-5">
              {lang === "ar" ? "تعديل الملف الشخصي" : "Edit Profile"}
            </h3>
            <form onSubmit={saveProfile} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>Instagram Handle</Label>
                  <Input
                    value={profileForm.instagram_handle}
                    onChange={(e) => setProfileForm((p) => ({ ...p, instagram_handle: e.target.value }))}
                    placeholder="@handle"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "عدد المتابعين" : "Followers"}</Label>
                  <Input
                    type="number"
                    value={profileForm.instagram_followers}
                    onChange={(e) => setProfileForm((p) => ({ ...p, instagram_followers: e.target.value }))}
                    placeholder="50000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "معدل التفاعل" : "Engagement Rate"}</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={profileForm.instagram_engagement_rate}
                    onChange={(e) => setProfileForm((p) => ({ ...p, instagram_engagement_rate: e.target.value }))}
                    placeholder="0.04"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "التخصص" : "Niche"}</Label>
                  <Input
                    value={profileForm.niche}
                    onChange={(e) => setProfileForm((p) => ({ ...p, niche: e.target.value }))}
                    placeholder="fashion, tech..."
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <Label>Rate/Post (JOD)</Label>
                  <Input
                    type="number"
                    value={profileForm.rate_per_post}
                    onChange={(e) => setProfileForm((p) => ({ ...p, rate_per_post: e.target.value }))}
                    placeholder="50"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Rate/Story (JOD)</Label>
                  <Input
                    type="number"
                    value={profileForm.rate_per_story}
                    onChange={(e) => setProfileForm((p) => ({ ...p, rate_per_story: e.target.value }))}
                    placeholder="30"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Rate/Reel (JOD)</Label>
                  <Input
                    type="number"
                    value={profileForm.rate_per_reel}
                    onChange={(e) => setProfileForm((p) => ({ ...p, rate_per_reel: e.target.value }))}
                    placeholder="80"
                  />
                </div>
              </div>

              <Button type="submit" disabled={saving}>
                {saving
                  ? lang === "ar" ? "جار الحفظ..." : "Saving..."
                  : lang === "ar" ? "حفظ الملف الشخصي" : "Save Profile"}
              </Button>
            </form>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
