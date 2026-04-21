import { BookingStatus } from "@/lib/types";
import { Lang } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const STEPS: {
  status: BookingStatus;
  labelEn: string;
  labelAr: string;
  doneStatuses: BookingStatus[];
}[] = [
  {
    status: "PENDING",
    labelEn: "Booking Created",
    labelAr: "تم الحجز",
    doneStatuses: ["CONFIRMED", "CONTENT_SUBMITTED", "CONTENT_APPROVED", "RELEASED"],
  },
  {
    status: "CONFIRMED",
    labelEn: "Influencer Confirmed",
    labelAr: "تأكيد من المؤثر",
    doneStatuses: ["CONTENT_SUBMITTED", "CONTENT_APPROVED", "RELEASED"],
  },
  {
    status: "CONTENT_SUBMITTED",
    labelEn: "Content Submitted",
    labelAr: "تقديم المحتوى",
    doneStatuses: ["CONTENT_APPROVED", "RELEASED"],
  },
  {
    status: "CONTENT_APPROVED",
    labelEn: "ARIA Review Passed",
    labelAr: "مراجعة ARIA",
    doneStatuses: ["RELEASED"],
  },
  {
    status: "RELEASED",
    labelEn: "Funds Released",
    labelAr: "تحويل المبلغ",
    doneStatuses: [],
  },
];

interface Props {
  currentStatus: BookingStatus;
  lang: Lang;
}

export function BookingTimeline({ currentStatus, lang }: Props) {
  return (
    <div className="booking-timeline">
      {STEPS.map((step, i) => {
        const isDone = step.doneStatuses.includes(currentStatus);
        const isActive = step.status === currentStatus;
        return (
          <div
            key={i}
            className={cn("timeline-item", isDone && "done", isActive && "active")}
          >
            <div className="timeline-dot" />
            <div className="flex-1">
              <div
                className={cn(
                  "text-sm font-medium",
                  isDone
                    ? "text-green-400"
                    : isActive
                    ? "text-violet-300"
                    : "text-white/40"
                )}
              >
                {lang === "ar" ? step.labelAr : step.labelEn}
              </div>
              {isDone && (
                <div className="text-[10px] text-green-400/60 mt-0.5">✓ Done</div>
              )}
              {isActive && (
                <div className="text-[10px] text-violet-400/60 mt-0.5">● Current</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
