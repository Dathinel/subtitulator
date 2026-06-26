import type { SubtitleStyle } from "../types";

interface Props {
  style: SubtitleStyle;
  sample: string;
}

const ALIGN: Record<SubtitleStyle["position"], string> = {
  top: "items-start pt-6",
  middle: "items-center",
  bottom: "items-end pb-6",
};

export function SubtitlePreview({ style, sample }: Props) {
  // Escala la fuente: el lienzo simula 1080p en un alto reducido.
  const scaled = Math.max(10, (style.font_size / 1080) * 240);

  return (
    <div className={`relative flex aspect-video w-full justify-center overflow-hidden rounded-xl bg-gradient-to-br from-ink-soft to-black ring-1 ring-ink-line ${ALIGN[style.position]}`}>
      <div className="pointer-events-none absolute inset-0 opacity-40 [background-image:radial-gradient(circle_at_30%_30%,rgba(245,177,61,0.12),transparent_40%),radial-gradient(circle_at_70%_70%,rgba(95,208,138,0.1),transparent_40%)]" />
      <span
        className="relative z-10 max-w-[88%] px-3 text-center font-bold leading-tight"
        style={{
          fontFamily: style.font,
          fontSize: `${scaled}px`,
          color: style.color,
          textShadow: `0 0 1px ${style.outline_color}, 1.5px 1.5px 0 ${style.outline_color}, -1.5px -1.5px 0 ${style.outline_color}, 1.5px -1.5px 0 ${style.outline_color}, -1.5px 1.5px 0 ${style.outline_color}`,
        }}
      >
        {sample || "Vista previa del subtítulo"}
      </span>
    </div>
  );
}
