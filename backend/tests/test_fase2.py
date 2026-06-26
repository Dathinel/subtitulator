import pytest
import os
import subprocess
import time
from pathlib import Path

from app.services.audio_service import (
    extraer_audio,
    obtener_duracion,
    AudioExtractionError,
    NoAudioTrackError,
)
from app.services.transcription_service import (
    transcribir,
    TranscriptionError,
)
from app.config import settings


TEST_VIDEO_CON_AUDIO = os.path.join(settings.TEMP_DIR, "test_video_con_audio.mp4")
TEST_VIDEO_SIN_AUDIO = os.path.join(settings.TEMP_DIR, "test_video_sin_audio.mp4")
TEST_AUDIO_WAV = os.path.join(settings.TEMP_DIR, "test_audio.wav")


@pytest.fixture(scope="session")
def generar_video_con_audio():
    """Genera un video de prueba de 5s con un tono sinusoidal de 440Hz."""
    cmd = [
        settings.FFMPEG_PATH,
        "-f", "lavfi",
        "-i", "color=c=black:s=320x240:d=5",
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=5",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-y",
        TEST_VIDEO_CON_AUDIO,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"No se pudo crear el video de prueba: {result.stderr}"
    yield TEST_VIDEO_CON_AUDIO
    if os.path.isfile(TEST_VIDEO_CON_AUDIO):
        os.remove(TEST_VIDEO_CON_AUDIO)


@pytest.fixture(scope="session")
def generar_video_sin_audio():
    """Genera un video de prueba sin pista de audio."""
    cmd = [
        settings.FFMPEG_PATH,
        "-f", "lavfi",
        "-i", "color=c=black:s=320x240:d=3",
        "-c:v", "libx264",
        "-an",
        "-y",
        TEST_VIDEO_SIN_AUDIO,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"No se pudo crear el video sin audio: {result.stderr}"
    yield TEST_VIDEO_SIN_AUDIO
    if os.path.isfile(TEST_VIDEO_SIN_AUDIO):
        os.remove(TEST_VIDEO_SIN_AUDIO)


class TestAudioService:
    def test_extraer_audio_exitoso(self, generar_video_con_audio):
        audio_path = extraer_audio(generar_video_con_audio)
        try:
            assert os.path.isfile(audio_path)
            assert os.path.getsize(audio_path) > 0
            assert audio_path.endswith(".wav")
        finally:
            if os.path.isfile(audio_path):
                os.remove(audio_path)

    def test_extraer_audio_archivo_inexistente(self):
        with pytest.raises(AudioExtractionError, match="no encontrado"):
            extraer_audio("/ruta/inexistente/video.mp4")

    def test_extraer_audio_video_sin_audio(self, generar_video_sin_audio):
        with pytest.raises(NoAudioTrackError, match="no contiene pista de audio"):
            extraer_audio(generar_video_sin_audio)

    def test_obtener_duracion(self, generar_video_con_audio):
        duracion = obtener_duracion(generar_video_con_audio)
        assert 4.5 <= duracion <= 5.5, f"Duracion esperada ~5s, obtenida: {duracion}"

    def test_obtener_duracion_archivo_inexistente(self):
        with pytest.raises(AudioExtractionError):
            obtener_duracion("/ruta/inexistente/video.mp4")

    def test_extraer_audio_tiene_formato_correcto(self, generar_video_con_audio):
        audio_path = extraer_audio(generar_video_con_audio)
        try:
            cmd = [settings.FFPROBE_PATH, "-v", "error", "-show_entries",
                   "stream=codec_name,sample_rate,channels",
                   "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            assert "16000" in lines, f"Sample rate esperado 16000 en {lines}"
            assert "1" in lines, f"Se esperaba 1 canal en {lines}"
        finally:
            if os.path.isfile(audio_path):
                os.remove(audio_path)


class TestTranscriptionService:
    def test_transcribir_archivo_inexistente(self):
        with pytest.raises(TranscriptionError, match="no encontrado"):
            transcribir("/ruta/inexistente/audio.wav")

    def test_transcribir_audio_con_tono(self, generar_video_con_audio):
        audio_path = extraer_audio(generar_video_con_audio)
        try:
            from app.services.transcription_service import EmptyTranscriptionError
            try:
                segmentos = transcribir(audio_path, idioma="en")
            except EmptyTranscriptionError:
                segmentos = []
            assert isinstance(segmentos, list)
        finally:
            if os.path.isfile(audio_path):
                os.remove(audio_path)

    def test_estructura_segmentos(self, generar_video_con_audio):
        audio_path = extraer_audio(generar_video_con_audio)
        try:
            from app.services.transcription_service import EmptyTranscriptionError
            try:
                segmentos = transcribir(audio_path, idioma="en")
            except EmptyTranscriptionError:
                segmentos = []
            for seg in segmentos:
                assert "inicio" in seg
                assert "fin" in seg
                assert "texto" in seg
                assert isinstance(seg["inicio"], float)
                assert isinstance(seg["fin"], float)
                assert isinstance(seg["texto"], str)
                assert seg["inicio"] < seg["fin"]
                assert seg["inicio"] >= 0
        finally:
            if os.path.isfile(audio_path):
                os.remove(audio_path)


class TestPipelineEndToEnd:
    def test_pipeline_completo(self, generar_video_con_audio):
        duracion = obtener_duracion(generar_video_con_audio)
        assert duracion > 0

        audio_path = extraer_audio(generar_video_con_audio)
        assert os.path.isfile(audio_path)

        try:
            from app.services.transcription_service import EmptyTranscriptionError
            try:
                segmentos = transcribir(audio_path, idioma="en")
            except EmptyTranscriptionError:
                segmentos = []
            assert isinstance(segmentos, list)
        finally:
            if os.path.isfile(audio_path):
                os.remove(audio_path)

    def test_limpieza_temporales(self, generar_video_con_audio):
        audio_path = extraer_audio(generar_video_con_audio)
        assert os.path.isfile(audio_path)
        if os.path.isfile(audio_path):
            os.remove(audio_path)
        assert not os.path.isfile(audio_path)
