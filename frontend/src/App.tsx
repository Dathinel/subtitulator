import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import type { Job } from "./types";
import { useJobPolling } from "./hooks/useJobPolling";
import { Logo } from "./components/Logo";
import { UploadView } from "./components/UploadView";
import { ProgressView } from "./components/ProgressView";
import { EditorView } from "./components/EditorView";
import { DownloadView } from "./components/DownloadView";
import { HistoryPanel } from "./components/HistoryPanel";

type Stage = "upload" | "processing" | "editing" | "rendering" | "done";

export default function App() {
  const [stage, setStage] = useState<Stage>("upload");
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [historyOpen, setHistoryOpen] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);

  const polledStages = stage === "processing" || stage === "rendering";
  const { job } = useJobPolling(polledStages ? jobId : null);

  // Transiciones automáticas según el estado del job sondeado.
  useEffect(() => {
    if (!job) return;
    if (stage === "processing" && job.status === "transcribed") setStage("editing");
    if (stage === "rendering" && job.status === "done") setStage("done");
    if (job.status === "error") setUploadError(job.error_message ?? "Error en el procesamiento");
  }, [job, stage]);

  const loadJobs = useCallback(async () => {
    setJobsLoading(true);
    try {
      setJobs(await api.listJobs());
    } finally {
      setJobsLoading(false);
    }
  }, []);

  async function handleUpload(file: File, language: string, model: string) {
    setBusy(true);
    setUploadError(null);
    try {
      const created = await api.createJob({ video: file, language, model });
      setJobId(created.id);
      setStage("processing");
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "No se pudo subir el vídeo");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setStage("upload");
    setJobId(null);
    setUploadError(null);
  }

  async function selectFromHistory(picked: Job) {
    setHistoryOpen(false);
    setJobId(picked.id);
    setUploadError(picked.status === "error" ? picked.error_message : null);
    if (picked.status === "done") setStage("done");
    else if (picked.status === "transcribed") setStage("editing");
    else if (picked.status === "rendering") setStage("rendering");
    else if (picked.status === "error") setStage("upload");
    else setStage("processing");
  }

  const activeJob = job ?? jobs.find((j) => j.id === jobId) ?? null;

  return (
    <div className="grain relative min-h-screen bg-studio">
      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <button onClick={reset} className="cursor-pointer">
          <Logo />
        </button>
        <button
          onClick={() => {
            setHistoryOpen(true);
            loadJobs();
          }}
          className="flex cursor-pointer items-center gap-2 rounded-lg border border-ink-line px-4 py-2 text-sm text-mist transition-colors duration-200 hover:border-signal/50 hover:text-signal"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M3 3v5h5M3.05 13A9 9 0 106 5.3L3 8" />
            <path d="M12 7v5l3 2" />
          </svg>
          Historial
        </button>
      </header>

      <main className="relative z-10 mx-auto flex max-w-6xl flex-col items-center px-6 pb-24 pt-6">
        {stage === "upload" && (
          <UploadView onSubmit={handleUpload} busy={busy} error={uploadError} />
        )}
        {stage === "processing" && activeJob && (
          <ProgressView job={activeJob} onCancel={reset} />
        )}
        {stage === "editing" && activeJob && (
          <EditorView job={activeJob} onRendering={() => setStage("rendering")} onCancel={reset} />
        )}
        {stage === "rendering" && activeJob && (
          <ProgressView job={activeJob} onCancel={reset} />
        )}
        {stage === "done" && activeJob && (
          <DownloadView job={activeJob} onReset={reset} />
        )}
      </main>

      <HistoryPanel
        open={historyOpen}
        jobs={jobs}
        loading={jobsLoading}
        onClose={() => setHistoryOpen(false)}
        onSelect={selectFromHistory}
      />
    </div>
  );
}
