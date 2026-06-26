import { motion } from "framer-motion";
import type { Job } from "../types";
import { STATUS_LABEL } from "../constants";

interface Props {
  job: Job;
  onCancel: () => void;
}

const STEPS = [
  { key: "upload", label: "Subida", at: 0 },
  { key: "audio", label: "Audio", at: 10 },
  { key: "transcribe", label: "Transcripción", at: 40 },
  { key: "ready", label: "Listo", at: 100 },
];

export function ProgressView({ job, onCancel }: Props) {
  const pct = Math.max(5, Math.min(100, job.progress));

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="mx-auto w-full max-w-xl text-center"
    >
      <p className="font-mono text-xs uppercase tracking-[0.4em] text-signal">paso 02 — proceso</p>
      <h2 className="mt-3 font-display text-3xl font-extrabold tracking-tight text-mist">
        {STATUS_LABEL[job.status] ?? job.status}
      </h2>
      <p className="mt-2 font-mono text-sm text-mist-dim">{job.original_filename}</p>

      <div className="mt-10">
        <div className="relative h-2 overflow-hidden rounded-full bg-ink-line">
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-signal-dim via-signal to-signal-bright"
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
          <div className="absolute inset-0 animate-shimmer bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent)] bg-[length:200%_100%]" />
        </div>
        <div className="mt-3 flex justify-between font-mono text-xs text-mist-dim">
          {STEPS.map((s) => (
            <span key={s.key} className={pct >= s.at ? "text-signal" : ""}>
              {s.label}
            </span>
          ))}
        </div>
      </div>

      <p className="mt-8 font-mono text-5xl font-bold text-mist tabular-nums">{pct}%</p>

      <button
        type="button"
        onClick={onCancel}
        className="mt-10 rounded-lg border border-ink-line px-4 py-2 text-sm text-mist-dim transition-colors duration-200 hover:border-mist-dim hover:text-mist"
      >
        Volver al inicio
      </button>
    </motion.div>
  );
}
