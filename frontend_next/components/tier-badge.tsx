import { Tier } from "@/lib/types";

const tierConfig: Record<
  Tier,
  { label: string; icon: string; className: string }
> = {
  PLATINUM: { label: "PLATINUM", icon: "🏆", className: "tier-platinum" },
  GOLD: { label: "GOLD", icon: "🥇", className: "tier-gold" },
  SILVER: { label: "SILVER", icon: "🥈", className: "tier-silver" },
  BRONZE: { label: "BRONZE", icon: "🥉", className: "tier-bronze" },
  UNRANKED: {
    label: "UNRANKED",
    icon: "—",
    className:
      "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-white/10 text-white/50",
  },
};

export function TierBadge({ tier }: { tier?: Tier }) {
  const cfg = tierConfig[tier ?? "UNRANKED"];
  return (
    <span className={cfg.className}>
      {cfg.icon} {cfg.label}
    </span>
  );
}
