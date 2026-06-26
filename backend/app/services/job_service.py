import json
import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.logger import get_logger
from app.repositories import job_repository
from app.schemas import JobStatus, SubtitleStyle, TranscriptPayload
from app.services.audio_service import extraer_audio, obtener_duracion
from app.services.render_service import quemar_subtitulos
from app.services.subtitle_service import generar_ass
from app.services.transcription_service import transcribir


logger = get_logger("job_service")


class JobServiceError(Exception):
    pass


def _job_dir(job_id: str) -> str:
    path = os.path.join(settings.JOBS_DIR, job_id)
    os.makedirs(path, exist_ok=True)
    return path


def _safe_filename(filename: str) -> str:
    return Path(filename).name.replace(" ", "_")


def _transcript_path(job_id: str) -> str:
    return os.path.join(_job_dir(job_id), "transcript.json")


def _write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _public_job(job: dict) -> dict:
    return {
        "id": job["id"],
        "original_filename": job["original_filename"],
        "language": job["language"],
        "model": job["model"],
        "status": job["status"],
        "progress": job["progress"],
        "error_message": job["error_message"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }


def _mark_error(job_id: str, message: str) -> None:
    logger.error("Job %s falló: %s", job_id, message)
    job_repository.update(
        job_id,
        status=JobStatus.error.value,
        error_message=message,
        progress=0,
    )


async def create_job(upload: UploadFile, language: str | None, model: str | None) -> dict:
    original_filename = upload.filename or "video"
    extension = Path(original_filename).suffix.lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Formatos permitidos: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}",
        )

    job_id = uuid.uuid4().hex
    job_path = _job_dir(job_id)
    input_path = os.path.join(job_path, f"input{extension}")

    size = 0
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    with open(input_path, "wb") as file:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > max_size:
                file.close()
                shutil.rmtree(job_path, ignore_errors=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"El archivo supera el límite de {settings.MAX_FILE_SIZE_MB} MB",
                )
            file.write(chunk)

    try:
        duration = obtener_duracion(input_path)
    except Exception as exc:
        shutil.rmtree(job_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"No se pudo leer el vídeo: {exc}") from exc

    if duration > settings.MAX_DURATION_SECONDS:
        shutil.rmtree(job_path, ignore_errors=True)
        raise HTTPException(
            status_code=400,
            detail=f"El vídeo supera el límite de duración de {settings.MAX_DURATION_SECONDS} segundos",
        )

    job = job_repository.create(
        {
            "id": job_id,
            "original_filename": _safe_filename(original_filename),
            "input_path": input_path,
            "language": language,
            "model": model or settings.WHISPER_MODEL,
        }
    )
    logger.info("Job %s creado (%s, idioma=%s, modelo=%s)", job_id, original_filename, language, model or settings.WHISPER_MODEL)
    return _public_job(job)


def get_job(job_id: str) -> dict:
    job = job_repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return _public_job(job)


def list_jobs() -> list[dict]:
    return [_public_job(job) for job in job_repository.list()]


def process_transcription(job_id: str) -> None:
    audio_path = None
    try:
        job = job_repository.get(job_id)
        if not job:
            return

        job_repository.update(
            job_id,
            status=JobStatus.processing.value,
            progress=10,
            error_message=None,
        )
        logger.info("Job %s: extrayendo audio", job_id)
        audio_path = extraer_audio(job["input_path"])
        job_repository.update(job_id, progress=40)

        logger.info("Job %s: transcribiendo", job_id)
        segments = transcribir(audio_path, job["language"])
        transcript_path = _transcript_path(job_id)
        _write_json(transcript_path, {"segmentos": segments})

        job_repository.update(
            job_id,
            status=JobStatus.transcribed.value,
            progress=100,
            transcript_path=transcript_path,
        )
        logger.info("Job %s: transcripción completada (%d segmentos)", job_id, len(segments))
    except Exception as exc:
        _mark_error(job_id, str(exc))
    finally:
        if audio_path and os.path.isfile(audio_path):
            os.remove(audio_path)


def get_transcript(job_id: str) -> dict:
    job = job_repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    if not job["transcript_path"] or not os.path.isfile(job["transcript_path"]):
        raise HTTPException(status_code=404, detail="Transcripción no disponible")
    data = _read_json(job["transcript_path"])
    return {"job_id": job_id, "segmentos": data.get("segmentos", [])}


def save_transcript(job_id: str, transcript: TranscriptPayload) -> dict:
    job = job_repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    if job["status"] not in {JobStatus.transcribed.value, JobStatus.rendering.value, JobStatus.done.value}:
        raise HTTPException(status_code=409, detail="La transcripción aún no está disponible")

    path = job["transcript_path"] or _transcript_path(job_id)
    payload = {"segmentos": [segment.model_dump() for segment in transcript.segmentos]}
    _write_json(path, payload)
    job_repository.update(job_id, transcript_path=path)
    return {"job_id": job_id, "segmentos": payload["segmentos"]}


def start_render(job_id: str) -> dict:
    job = job_repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    if job["status"] not in {JobStatus.transcribed.value, JobStatus.done.value}:
        raise HTTPException(status_code=409, detail="El job debe estar transcrito antes de renderizar")
    updated = job_repository.update(
        job_id,
        status=JobStatus.rendering.value,
        progress=10,
        error_message=None,
    )
    return _public_job(updated)


def render_job(job_id: str, style: SubtitleStyle) -> None:
    try:
        job = job_repository.get(job_id)
        if not job:
            return
        if not job["transcript_path"] or not os.path.isfile(job["transcript_path"]):
            raise JobServiceError("Transcripción no disponible para renderizar")

        transcript = _read_json(job["transcript_path"])
        subtitles_path = os.path.join(_job_dir(job_id), "subtitles.ass")
        output_path = os.path.join(_job_dir(job_id), "output.mp4")

        generar_ass(transcript.get("segmentos", []), style, subtitles_path)
        job_repository.update(job_id, progress=50, subtitles_path=subtitles_path)

        logger.info("Job %s: quemando subtítulos", job_id)
        quemar_subtitulos(job["input_path"], subtitles_path, output_path)
        job_repository.update(
            job_id,
            status=JobStatus.done.value,
            progress=100,
            output_path=output_path,
        )
        logger.info("Job %s: render completado", job_id)
    except Exception as exc:
        _mark_error(job_id, str(exc))


def get_download_path(job_id: str) -> str:
    job = job_repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    if job["status"] != JobStatus.done.value or not job["output_path"] or not os.path.isfile(job["output_path"]):
        raise HTTPException(status_code=404, detail="Vídeo renderizado no disponible")
    return job["output_path"]
