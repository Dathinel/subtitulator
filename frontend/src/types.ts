export type JobStatus =
  | "pending"
  | "processing"
  | "transcribed"
  | "rendering"
  | "done"
  | "error";

export interface Job {
  id: string;
  original_filename: string;
  language: string | null;
  model: string;
  status: JobStatus;
  progress: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface TranscriptSegment {
  inicio: number;
  fin: number;
  texto: string;
}

export interface TranscriptResponse {
  job_id: string;
  segmentos: TranscriptSegment[];
}

export type SubtitlePosition = "top" | "middle" | "bottom";

export interface SubtitleStyle {
  font: string;
  font_size: number;
  color: string;
  outline_color: string;
  position: SubtitlePosition;
}
