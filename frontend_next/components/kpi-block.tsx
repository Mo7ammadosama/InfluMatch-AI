import { cn } from "@/lib/utils";

interface Props {
  label: string;
  value: string | number;
  sub?: string;
  accent?: "violet" | "amber" | "green" | "red" | "blue";
  className?: string;
}

const accentColors = {
  violet: "text-violet-400",
  amber: "text-amber-400",
  green: "text-green-400",
  red: "text-red-400",
  blue: "text-blue-400",
};

export function KpiBlock({ label, value, sub, accent = "violet", className }: Props) {
  return (
    <div className={cn("kpi-block", className)}>
      <div className={cn("kpi-value", accentColors[accent])}>{value}</div>
      <div className="kpi-label">{label}</div>
      {sub && <div className="text-xs text-white/30 mt-1">{sub}</div>}
    </div>
  );
}
