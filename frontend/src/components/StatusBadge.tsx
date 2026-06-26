import type { JobStatus } from "../types";
import { STATUS_LABEL } from "../constants";

const TONE: Record<JobStatus, string> = {
  pending: "bg-mist-dim/10 text-mist-dim ring-mist-dim/30",
  processing: "bg-signal/10 text-signal ring-signal/30",
  transcribed: "bg-signal/10 text-signal-bright ring-signal/40",
  rendering: "bg-signal/10 text-signal ring-signal/30",
  done: "bg-good/10 text-good ring-good/30",
  error: "bg-danger/10 text-danger ring-danger/30",
};

const ACTIVE: JobStatus[] = ["pending", "processing", "rendering"];

export function StatusBadge({ status }: { status: JobStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${TONE[status]}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full bg-current ${ACTIVE.includes(status) ? "animate-pulse" : ""}`}
      />
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}
