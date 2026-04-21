import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmtJOD(amount: number | null | undefined): string {
  return `${(amount ?? 0).toFixed(2)} JOD`;
}

export function fmtNum(n: number | null | undefined): string {
  const v = n ?? 0;
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  return String(v);
}

export function statusClass(status: string): string {
  const map: Record<string, string> = {
    PENDING: "status-pending",
    ACTIVE: "status-active",
    CONFIRMED: "status-confirmed",
    COMPLETED: "status-completed",
    RELEASED: "status-completed",
    DISPUTED: "status-disputed",
    DRAFT: "status-pending",
    IN_PROGRESS: "status-active",
    CONTENT_SUBMITTED: "status-confirmed",
    CONTENT_APPROVED: "status-active",
  };
  return map[status] ?? "status-pending";
}
