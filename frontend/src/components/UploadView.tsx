import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { LANGUAGES, MODELS } from "../constants";

interface Props {
  onSubmit: (file: File, language: string, model: string) => void;
  busy: boolean;
  error: string | null;
}

const ACCEPT = ".mp4,.mov,.mkv,.avi,.webm";

export function UploadView({ onSubmit, busy, error }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("auto");
  const [model, setModel] = useState("small");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function pick(f: File | null) {
    if (f) setFile(f);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="mx-auto w-full max-w-2xl"
    >
      <div className="mb-8 text-center">
        <p className="font-mono text-xs uppercase tracking-[0.4em] text-signal">paso 01 — fuente</p>
        <h1 className="mt-3 font-display text-4xl font-extrabold tracking-tight text-mist sm:text-5xl">
          Da voz a tu vídeo.
        </h1>
        <p className="mx-auto mt-3 max-w-md text-mist-dim">
          Sube un vídeo sin subtítulos. Transcribimos el audio, lo revisas y lo
          quemamos en la imagen.
        </p>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          pick(e.dataTransfer.files?.[0] ?? null);
        }}
        onClick={() => inputRef.current?.click()}
        className={`group relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed bg-ink-card/60 px-8 py-12 text-center transition-colors duration-200 ${
          dragging ? "border-signal bg-signal/5" : "border-ink-line hover:border-signal/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          className="hidden"
          onChange={(e) => pick(e.target.files?.[0] ?? null)}
        />
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-signal/10 ring-1 ring-signal/25">
          <svg viewBox="0 0 24 24" className="h-6 w-6 text-signal" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 16V4m0 0l-4 4m4-4l4 4" />
            <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
          </svg>
        </div>
        {file ? (
          <p className="font-mono text-sm text-mist">
            {file.name} <span className="text-mist-dim">· {(file.size / 1048576).toFixed(1)} MB</span>
          </p>
        ) : (
          <>
            <p className="font-medium text-mist">Arrastra un vídeo o haz clic para elegirlo</p>
            <p className="mt-1 font-mono text-xs text-mist-dim">mp4 · mov · mkv · avi · webm · máx. 500 MB</p>
          </>
        )}
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Field label="Idioma del audio">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="select"
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Modelo de transcripción">
          <select value={model} onChange={(e) => setModel(e.target.value)} className="select">
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label} — {m.hint}
              </option>
            ))}
          </select>
        </Field>
      </div>

      {error && (
        <p className="mt-4 rounded-lg bg-danger/10 px-4 py-3 text-sm text-danger ring-1 ring-danger/30">
          {error}
        </p>
      )}

      <button
        type="button"
        disabled={!file || busy}
        onClick={() => file && onSubmit(file, language, model)}
        className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-signal px-6 py-4 font-display text-base font-bold text-ink transition-colors duration-200 hover:bg-signal-bright disabled:cursor-not-allowed disabled:opacity-40"
      >
        {busy ? "Subiendo…" : "Transcribir vídeo"}
        {!busy && (
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 12h14m-6-6l6 6-6 6" />
          </svg>
        )}
      </button>
    </motion.div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block font-mono text-xs uppercase tracking-wider text-mist-dim">{label}</span>
      {children}
    </label>
  );
}
