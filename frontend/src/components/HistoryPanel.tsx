import { AnimatePresence, motion } from "framer-motion";
import type { Job } from "../types";
import { StatusBadge } from "./StatusBadge";

interface Props {
  open: boolean;
  jobs: Job[];
  loading: boolean;
  onClose: () => void;
  onSelect: (job: Job) => void;
}

function relative(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.round(diff / 60000);
  if (min < 1) return "ahora";
  if (min < 60) return `hace ${min} min`;
  const h = Math.round(min / 60);
  if (h < 24) return `hace ${h} h`;
  return `hace ${Math.round(h / 24)} d`;
}

export function HistoryPanel({ open, jobs, loading, onClose, onSelect }: Props) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-black/60"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-ink-line bg-ink-soft"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 280 }}
          >
            <header className="flex items-center justify-between border-b border-ink-line px-6 py-5">
              <h2 className="font-display text-xl font-bold text-mist">Historial</h2>
              <button
                onClick={onClose}
                className="cursor-pointer rounded-lg p-1.5 text-mist-dim transition-colors hover:bg-ink-card hover:text-mist"
                aria-label="Cerrar historial"
              >
                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </header>

            <div className="flex-1 overflow-y-auto px-4 py-4">
              {loading && <p className="p-4 text-center font-mono text-sm text-mist-dim">Cargando…</p>}
              {!loading && jobs.length === 0 && (
                <p className="p-8 text-center text-sm text-mist-dim">Aún no has procesado vídeos.</p>
              )}
              <ul className="space-y-2">
                {jobs.map((job) => (
                  <li key={job.id}>
                    <button
                      onClick={() => onSelect(job)}
                      className="w-full cursor-pointer rounded-xl border border-ink-line bg-ink-card/50 p-4 text-left transition-colors duration-200 hover:border-signal/40"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="truncate font-medium text-mist">{job.original_filename}</span>
                        <StatusBadge status={job.status} />
                      </div>
                      <div className="mt-2 flex items-center gap-3 font-mono text-xs text-mist-dim">
                        <span>{relative(job.created_at)}</span>
                        <span>·</span>
                        <span>{job.model}</span>
                        {job.language && <span>· {job.language}</span>}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
