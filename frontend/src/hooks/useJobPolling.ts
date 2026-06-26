import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { Job } from "../types";

const ACTIVE: Job["status"][] = ["pending", "processing", "rendering"];

/**
 * Sondea (polling) el estado de un job mientras esté activo.
 * Se detiene al alcanzar transcribed/done/error.
 */
export function useJobPolling(jobId: string | null, intervalMs = 2000) {
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;

    async function tick() {
      try {
        const next = await api.getJob(jobId!);
        if (cancelled) return;
        setJob(next);
        setError(null);
        if (ACTIVE.includes(next.status)) {
          timer.current = window.setTimeout(tick, intervalMs);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Error de conexión");
        timer.current = window.setTimeout(tick, intervalMs * 2);
      }
    }

    tick();
    return () => {
      cancelled = true;
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [jobId, intervalMs]);

  return { job, error, setJob };
}
