"use client";

import { InfluencerProfile } from "@/lib/types";
import { AriaScoreRing } from "./aria-score-ring";
import { TierBadge } from "./tier-badge";
import { Button } from "./ui/button";
import { fmtNum, fmtJOD } from "@/lib/utils";
import { MapPin, AtSign } from "lucide-react";
import { Lang, tr } from "@/lib/i18n";

interface Props {
  influencer: InfluencerProfile;
  lang: Lang;
  onBook?: (influencer: InfluencerProfile) => void;
}

export function InfluencerCard({ influencer, lang, onBook }: Props) {
  const score = influencer.aria_score ?? 0;
  const igPlatform = influencer.social_platforms?.instagram;
  const handle = igPlatform?.handle ?? influencer.display_name;
  const followers = igPlatform?.followers ?? influencer.total_followers ?? 0;
  const engagementRate = igPlatform?.engagement_rate ?? influencer.avg_engagement_rate ?? 0;
  const niche = influencer.content_categories?.[0] ?? "";

  return (
    <div className="inf-card flex flex-col">
      <div className="p-4 flex-1">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <AtSign size={14} className="text-violet-400 flex-shrink-0" />
              <span className="text-white font-semibold text-sm truncate">
                {handle ?? "—"}
              </span>
            </div>
            <div className="flex items-center gap-1 mt-1">
              <MapPin size={11} className="text-white/30" />
              <span className="text-xs text-white/40">{influencer.city ?? "—"}</span>
            </div>
            <div className="mt-1.5">
              <TierBadge tier={influencer.aria_tier} />
            </div>
          </div>
          <AriaScoreRing score={score} size="sm" />
        </div>

        {/* Category/niche */}
        {niche && (
          <div className="text-xs text-violet-400 font-medium mb-3 capitalize">
            #{niche}
          </div>
        )}

        {/* Stats grid */}
        <div className="stats-grid mb-3">
          <div className="stats-grid-item">
            <div className="text-white text-sm font-bold">
              {fmtNum(followers)}
            </div>
            <div className="text-white/40 text-[10px]">{tr("followers", lang)}</div>
          </div>
          <div className="stats-grid-item">
            <div className="text-green-400 text-sm font-bold">
              {(engagementRate * 100).toFixed(1)}%
            </div>
            <div className="text-white/40 text-[10px]">{tr("engagement", lang)}</div>
          </div>
          <div className="stats-grid-item">
            <div className="text-amber-400 text-sm font-bold">
              {fmtJOD(influencer.rate_per_post_jod ?? 0)}
            </div>
            <div className="text-white/40 text-[10px]">{tr("rate_per_post", lang)}</div>
          </div>
          <div className="stats-grid-item">
            <div className="text-violet-400 text-sm font-bold">{score}</div>
            <div className="text-white/40 text-[10px]">ARIA</div>
          </div>
        </div>

        {/* Match score */}
        {influencer.match_score != null && (
          <div className="text-xs text-green-400 font-medium mb-1">
            {Math.round(influencer.match_score * 100)}% match
          </div>
        )}

        {/* Availability */}
        <div
          className={`text-xs font-medium ${
            influencer.is_available ? "text-green-400" : "text-red-400"
          }`}
        >
          {influencer.is_available
            ? lang === "ar" ? "متاح" : "Available"
            : lang === "ar" ? "غير متاح" : "Unavailable"}
        </div>
      </div>

      {onBook && influencer.is_available && (
        <div className="px-4 pb-4">
          <Button
            variant="default"
            size="sm"
            className="w-full"
            onClick={() => onBook(influencer)}
          >
            📅 {tr("book_now", lang)}
          </Button>
        </div>
      )}
    </div>
  );
}
