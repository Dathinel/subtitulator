from faster_whisper import WhisperModel
from app.config import settings
import os


class TranscriptionError(Exception):
    pass


class EmptyTranscriptionError(TranscriptionError):
    pass


_modelo = None  # Singleton del modelo


def _obtener_modelo() -> WhisperModel:
    global _modelo
    if _modelo is None:
        os.makedirs(settings.MODEL_DIR, exist_ok=True)
        _modelo = WhisperModel(
            settings.WHISPER_MODEL,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
            download_root=settings.MODEL_DIR,
        )
    return _modelo


def transcribir(audio_path: str, idioma: str | None = None) -> list[dict]:
    if not os.path.isfile(audio_path):
        raise TranscriptionError(f"Archivo de audio no encontrado: {audio_path}")

    try:
        modelo = _obtener_modelo()
        segments, info = modelo.transcribe(
            audio_path,
            language=idioma,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=300,
            ),
        )

        segmentos = []
        for segment in segments:
            segmentos.append({
                "inicio": round(segment.start, 3),
                "fin": round(segment.end, 3),
                "texto": segment.text.strip(),
            })

        if not segmentos:
            raise EmptyTranscriptionError(
                "La transcripcion no produjo ningun segmento. "
                "El audio podria no contener voz o el idioma no coincide."
            )

        return segmentos

    except (EmptyTranscriptionError, TranscriptionError):
        raise
    except Exception as e:
        raise TranscriptionError(f"Error durante la transcripcion: {str(e)}") from e
