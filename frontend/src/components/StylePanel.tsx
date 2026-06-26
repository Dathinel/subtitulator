import type { SubtitlePosition, SubtitleStyle } from "../types";
import { FONTS } from "../constants";

interface Props {
  style: SubtitleStyle;
  onChange: (next: SubtitleStyle) => void;
}

const POSITIONS: { value: SubtitlePosition; label: string }[] = [
  { value: "top", label: "Arriba" },
  { value: "middle", label: "Centro" },
  { value: "bottom", label: "Abajo" },
];

export function StylePanel({ style, onChange }: Props) {
  const set = <K extends keyof SubtitleStyle>(key: K, value: SubtitleStyle[K]) =>
    onChange({ ...style, [key]: value });

  return (
    <div className="space-y-5">
      <label className="block">
        <span className="mb-2 block font-mono text-xs uppercase tracking-wider text-mist-dim">Fuente</span>
        <select className="select" value={style.font} onChange={(e) => set("font", e.target.value)}>
          {FONTS.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
      </label>

      <label className="block">
        <span className="mb-2 flex items-center justify-between font-mono text-xs uppercase tracking-wider text-mist-dim">
          Tamaño <span className="text-signal">{style.font_size}px</span>
        </span>
        <input
          type="range"
          min={12}
          max={120}
          value={style.font_size}
          onChange={(e) => set("font_size", Number(e.target.value))}
          className="w-full"
        />
      </label>

      <div className="grid grid-cols-2 gap-4">
        <ColorField label="Texto" value={style.color} onChange={(v) => set("color", v)} />
        <ColorField label="Borde" value={style.outline_color} onChange={(v) => set("outline_color", v)} />
      </div>

      <div>
        <span className="mb-2 block font-mono text-xs uppercase tracking-wider text-mist-dim">Posición</span>
        <div className="grid grid-cols-3 gap-2">
          {POSITIONS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => set("position", p.value)}
              className={`cursor-pointer rounded-lg border px-3 py-2 text-sm transition-colors duration-200 ${
                style.position === p.value
                  ? "border-signal bg-signal/10 text-signal"
                  : "border-ink-line text-mist-dim hover:border-mist-dim hover:text-mist"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="mb-2 block font-mono text-xs uppercase tracking-wider text-mist-dim">{label}</span>
      <div className="flex items-center gap-2 rounded-lg border border-ink-line bg-ink-soft p-1.5">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value.toUpperCase())}
          className="h-8 w-8 cursor-pointer rounded border-0 bg-transparent p-0"
          aria-label={`Color ${label}`}
        />
        <span className="font-mono text-xs text-mist">{value}</span>
      </div>
    </label>
  );
}
