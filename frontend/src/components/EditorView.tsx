import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "../api/client";
import { DEFAULT_STYLE } from "../constants";
import type { Job, SubtitleStyle, TranscriptSegment } from "../types";
import { TranscriptEditor } from "./TranscriptEditor";
import { StylePanel } from "./StylePanel";
import { SubtitlePreview } from "./SubtitlePreview";

interface Props {
  job: Job;
  onRendering: () => void;
  onCancel: () => void;
}

export function EditorView({ job, onRendering, onCancel }: Props) {
  const [segments, setSegments] = useState<TranscriptSegment[] | null>(null);
  const [style, setStyle] = useState<SubtitleStyle>(DEFAULT_STYLE);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .getTranscript(job.id)
      .then((res) => !cancelled && setSegments(res.segmentos))
      .catch((err) => !cancelled && setLoadError(err instanceof Error ? err.message : "Error al cargar"));
    return () => {
      cancelled = true;
    };
  }, [job.id]);

  async function save() {
    if (!segments) return;
    setSaving(true);
    setActionError(null);
    try {
      const res = await api.saveTranscript(job.id, segments);
      setSegments(res.segmentos);
      setSavedAt(Date.now());
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No se pudo guardar");
    } finally {
      setSaving(false);
    }
  }

  async function render() {
    if (!segments) return;
    setRendering(true);
    setActionError(null);
    try {
      await api.saveTranscript(job.id, segments);
      await api.render(job.id, style);
      onRendering();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No se pudo renderizar");
      setRendering(false);
    }
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-md rounded-xl bg-danger/10 p-6 text-center text-danger ring-1 ring-danger/30">
        {loadError}
        <button onClick={onCancel} className="mt-4 block w-full rounded-lg border border-danger/40 py-2 text-sm">
          Volver
        </button>
      </div>
    );
  }

  if (!segments) {
    return <p className="text-center font-mono text-sm text-mist-dim">Cargando transcripción…</p>;
  }

  const sample = segments[activeIndex]?.texto ?? segments[0]?.texto ?? "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="w-full"
    >
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.4em] text-signal">paso 03 — revisión</p>
          <h2 className="mt-2 font-display text-3xl font-extrabold tracking-tight text-mist">
            Revisa y da estilo
          </h2>
        </div>
        <p className="font-mono text-xs text-mist-dim">{segments.length} segmentos · {job.original_filename}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <section className="card p-4">
          <h3 className="mb-3 font-mono text-xs uppercase tracking-wider text-mist-dim">Transcripción</h3>
          <div className="max-h-[60vh] overflow-y-auto pr-1">
            <TranscriptEditor
              segments={segments}
              activeIndex={activeIndex}
              onChange={setSegments}
              onFocusSegment={setActiveIndex}
            />
          </div>
        </section>

        <section className="space-y-6">
          <div className="card p-4">
            <h3 className="mb-3 font-mono text-xs uppercase tracking-wider text-mist-dim">Vista previa</h3>
            <SubtitlePreview style={style} sample={sample} />
          </div>
          <div className="card p-4">
            <h3 className="mb-4 font-mono text-xs uppercase tracking-wider text-mist-dim">Estilo</h3>
            <StylePanel style={style} onChange={setStyle} />
          </div>
        </section>
      </div>

      {actionError && (
        <p className="mt-4 rounded-lg bg-danger/10 px-4 py-3 text-sm text-danger ring-1 ring-danger/30">{actionError}</p>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={save}
          disabled={saving || rendering}
          className="cursor-pointer rounded-xl border border-ink-line px-5 py-3 text-sm font-medium text-mist transition-colors duration-200 hover:border-mist-dim disabled:opacity-40"
        >
          {saving ? "Guardando…" : "Guardar cambios"}
        </button>
        {savedAt && <span className="font-mono text-xs text-good">Guardado ✓</span>}
        <button
          type="button"
          onClick={render}
          disabled={rendering || segments.length === 0}
          className="ml-auto flex cursor-pointer items-center gap-2 rounded-xl bg-signal px-6 py-3 font-display text-base font-bold text-ink transition-colors duration-200 hover:bg-signal-bright disabled:cursor-not-allowed disabled:opacity-40"
        >
          {rendering ? "Enviando…" : "Quemar subtítulos"}
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 12h14m-6-6l6 6-6 6" />
          </svg>
        </button>
      </div>
    </motion.div>
  );
}
