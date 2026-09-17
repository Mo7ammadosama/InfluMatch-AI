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
    status: "proposed",
    labelEn: "Booking Created",
    labelAr: "تم الحجز",
    doneStatuses: ["accepted", "in_progress", "content_submitted", "content_approved", "amount_transferred", "published", "completed"],
  },
  {
    status: "accepted",
    labelEn: "Influencer Confirmed",
    labelAr: "تأكيد من المؤثر",
    doneStatuses: ["in_progress", "content_submitted", "content_approved", "amount_transferred", "published", "completed"],
  },
  {
    status: "content_submitted",
    labelEn: "Content Submitted",
    labelAr: "تقديم المحتوى",
    doneStatuses: ["content_approved", "amount_transferred", "published", "completed"],
  },
  {
    status: "content_approved",
    labelEn: "Content Approved",
    labelAr: "الموافقة على المحتوى",
    doneStatuses: ["amount_transferred", "published", "completed"],
  },
  {
    status: "amount_transferred",
    labelEn: "Funds Released",
    labelAr: "تحويل المبلغ",
    doneStatuses: ["published", "completed"],
  },
  {
    status: "completed",
    labelEn: "Completed",
    labelAr: "مكتملة",
    doneStatuses: [],
  },
];

interface Props {
  currentStatus: string;
  lang: Lang;
}

export function BookingTimeline({ currentStatus, lang }: Props) {
  return (
    <div className="booking-timeline">
      {STEPS.map((step, i) => {
        const isDone = step.doneStatuses.includes(currentStatus as BookingStatus);
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
                  isDone ? "text-green-400" : isActive ? "text-violet-300" : "text-white/40"
                )}
              >
                {lang === "ar" ? step.labelAr : step.labelEn}
              </div>
              {isDone && <div className="text-[10px] text-green-400/60 mt-0.5">✓ Done</div>}
              {isActive && <div className="text-[10px] text-violet-400/60 mt-0.5">● Current</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
