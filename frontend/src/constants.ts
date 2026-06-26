import type { SubtitleStyle } from "./types";

export const LANGUAGES: { code: string; label: string }[] = [
  { code: "auto", label: "Detección automática" },
  { code: "es", label: "Español" },
  { code: "en", label: "Inglés" },
  { code: "fr", label: "Francés" },
  { code: "de", label: "Alemán" },
  { code: "it", label: "Italiano" },
  { code: "pt", label: "Portugués" },
  { code: "ca", label: "Catalán" },
  { code: "gl", label: "Gallego" },
  { code: "eu", label: "Euskera" },
  { code: "nl", label: "Neerlandés" },
  { code: "ru", label: "Ruso" },
  { code: "zh", label: "Chino" },
  { code: "ja", label: "Japonés" },
  { code: "ko", label: "Coreano" },
  { code: "ar", label: "Árabe" },
];

export const MODELS: { value: string; label: string; hint: string }[] = [
  { value: "tiny", label: "Tiny", hint: "El más rápido · calidad baja" },
  { value: "base", label: "Base", hint: "Rápido · calidad aceptable" },
  { value: "small", label: "Small", hint: "Equilibrio recomendado" },
  { value: "medium", label: "Medium", hint: "Lento en CPU · más calidad" },
];

export const FONTS = ["Arial", "Helvetica", "Verdana", "Georgia", "Courier New", "Impact"];

export const DEFAULT_STYLE: SubtitleStyle = {
  font: "Arial",
  font_size: 48,
  color: "#FFFFFF",
  outline_color: "#000000",
  position: "bottom",
};

export const STATUS_LABEL: Record<string, string> = {
  pending: "En cola",
  processing: "Transcribiendo",
  transcribed: "Listo para revisar",
  rendering: "Renderizando",
  done: "Completado",
  error: "Error",
};
