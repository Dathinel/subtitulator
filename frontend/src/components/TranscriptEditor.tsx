import type { TranscriptSegment } from "../types";
import { formatTimecode, parseTimecode } from "../utils/time";

interface Props {
  segments: TranscriptSegment[];
  activeIndex: number;
  onChange: (next: TranscriptSegment[]) => void;
  onFocusSegment: (index: number) => void;
}

export function TranscriptEditor({ segments, activeIndex, onChange, onFocusSegment }: Props) {
  function update(index: number, patch: Partial<TranscriptSegment>) {
    onChange(segments.map((s, i) => (i === index ? { ...s, ...patch } : s)));
  }

  function remove(index: number) {
    onChange(segments.filter((_, i) => i !== index));
  }

  return (
    <div className="space-y-2">
      {segments.map((seg, i) => (
        <div
          key={i}
          onFocus={() => onFocusSegment(i)}
          onMouseEnter={() => onFocusSegment(i)}
          className={`group rounded-xl border p-3 transition-colors duration-200 ${
            i === activeIndex ? "border-signal/50 bg-signal/5" : "border-ink-line bg-ink-soft/40 hover:border-ink-line/80"
          }`}
        >
          <div className="mb-2 flex items-center gap-2">
            <TimeInput value={seg.inicio} onCommit={(v) => update(i, { inicio: v })} />
            <span className="text-mist-dim">→</span>
            <TimeInput value={seg.fin} onCommit={(v) => update(i, { fin: v })} />
            <span className="ml-auto font-mono text-[10px] text-mist-dim">#{i + 1}</span>
            <button
              type="button"
              onClick={() => remove(i)}
              className="cursor-pointer rounded p-1 text-mist-dim opacity-0 transition-opacity duration-200 hover:text-danger group-hover:opacity-100"
              aria-label={`Eliminar segmento ${i + 1}`}
            >
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>
          <textarea
            value={seg.texto}
            onChange={(e) => update(i, { texto: e.target.value })}
            rows={2}
            className="input resize-none font-body text-sm leading-relaxed"
          />
        </div>
      ))}
      {segments.length === 0 && (
        <p className="rounded-xl border border-dashed border-ink-line p-6 text-center text-sm text-mist-dim">
          No hay segmentos en la transcripción.
        </p>
      )}
    </div>
  );
}

function TimeInput({ value, onCommit }: { value: number; onCommit: (v: number) => void }) {
  return (
    <input
      defaultValue={formatTimecode(value)}
      key={value}
      onBlur={(e) => {
        const parsed = parseTimecode(e.target.value);
        if (parsed !== null) onCommit(parsed);
        else e.target.value = formatTimecode(value);
      }}
      className="w-20 rounded border border-ink-line bg-ink px-2 py-1 text-center font-mono text-xs text-signal outline-none focus:border-signal/60"
      aria-label="Marca de tiempo"
    />
  );
}
