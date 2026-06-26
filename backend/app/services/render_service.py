import os
import subprocess

from app.config import settings
from app.logger import get_logger

logger = get_logger("render_service")


class RenderError(Exception):
    pass


def _escape_filter_path(path: str) -> str:
    normalized = os.path.abspath(path).replace("\\", "/")
    return normalized.replace(":", "\\:")


def quemar_subtitulos(video_path: str, subtitles_path: str, output_path: str) -> str:
    if not os.path.isfile(video_path):
        raise RenderError(f"Archivo de vídeo no encontrado: {video_path}")
    if not os.path.isfile(subtitles_path):
        raise RenderError(f"Archivo de subtítulos no encontrado: {subtitles_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        settings.FFMPEG_PATH,
        "-y",
        "-i",
        video_path,
        "-vf",
        f"ass='{_escape_filter_path(subtitles_path)}'",
        "-c:a",
        "copy",
        output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=getattr(settings, "FFMPEG_TIMEOUT", 600),
        )
    except subprocess.TimeoutExpired as exc:
        raise RenderError("Timeout al renderizar el vídeo con FFmpeg") from exc

    if result.returncode != 0:
        message = result.stderr.strip() or "FFmpeg falló al renderizar el vídeo"
        logger.error("FFmpeg (render) stderr: %s", message)
        raise RenderError(message)

    if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
        raise RenderError("FFmpeg no generó un vídeo de salida válido")

    return output_path
