import subprocess
import os
import uuid
from pathlib import Path
from app.config import settings
from app.logger import get_logger

logger = get_logger("audio_service")


class AudioExtractionError(Exception):
    pass


class NoAudioTrackError(AudioExtractionError):
    pass


def _tiene_pista_audio(video_path: str) -> bool:
    cmd = [
        settings.FFPROBE_PATH,
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and "audio" in result.stdout.lower()


def extraer_audio(video_path: str, output_dir: str = None) -> str:
    if not os.path.isfile(video_path):
        raise AudioExtractionError(f"Archivo de video no encontrado: {video_path}")

    if not _tiene_pista_audio(video_path):
        raise NoAudioTrackError(
            f"El video no contiene pista de audio: {video_path}"
        )

    output_dir = output_dir or settings.TEMP_DIR
    os.makedirs(output_dir, exist_ok=True)

    audio_filename = f"{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(output_dir, audio_filename)

    probar_codecs = ["pcm_s16le", "aac"]

    ultimo_error = None
    for codec in probar_codecs:
        cmd = [
            settings.FFMPEG_PATH,
            "-i", video_path,
            "-vn",
            "-acodec", codec,
            "-ar", "16000",
            "-ac", "1",
            "-y",
            audio_path,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=getattr(settings, 'FFMPEG_TIMEOUT', 300),
            )

            if result.returncode == 0 and os.path.isfile(audio_path) and os.path.getsize(audio_path) > 0:
                return audio_path

            ultimo_error = result.stderr.strip()
            if os.path.isfile(audio_path):
                os.remove(audio_path)

        except subprocess.TimeoutExpired:
            ultimo_error = "Timeout al extraer audio con FFmpeg"
            if os.path.isfile(audio_path):
                os.remove(audio_path)
            raise AudioExtractionError(ultimo_error)

    logger.error("FFmpeg (audio) stderr: %s", ultimo_error)
    raise AudioExtractionError(f"FFmpeg fallo al extraer audio: {ultimo_error}")


def obtener_duracion(video_path: str) -> float:
    if not os.path.isfile(video_path):
        raise AudioExtractionError(f"Archivo de video no encontrado: {video_path}")

    cmd = [
        settings.FFPROBE_PATH,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        pass

    raise AudioExtractionError(f"No se pudo determinar la duracion del video: {video_path}")
