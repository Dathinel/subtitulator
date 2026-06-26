/** Convierte segundos a timecode mm:ss.cc para mostrar en el editor. */
export function formatTimecode(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) seconds = 0;
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const cs = Math.round((seconds - Math.floor(seconds)) * 100);
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
}

/** Convierte un timecode mm:ss.cc (o ss.cc) a segundos. Devuelve null si es inválido. */
export function parseTimecode(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const match = trimmed.match(/^(?:(\d+):)?(\d{1,2})(?:\.(\d{1,2}))?$/);
  if (!match) return null;
  const minutes = match[1] ? Number(match[1]) : 0;
  const secs = Number(match[2]);
  const cs = match[3] ? Number(match[3].padEnd(2, "0")) : 0;
  if (secs > 59) return null;
  return minutes * 60 + secs + cs / 100;
}
