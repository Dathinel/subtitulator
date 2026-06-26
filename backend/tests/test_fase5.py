import logging

from fastapi.testclient import TestClient

from app.config import settings
from app.logger import get_logger
from app.main import app
from app.services import job_service


client = TestClient(app)


class TestValidacionEntrada:
    def test_formato_no_soportado_retorna_400(self):
        response = client.post(
            "/jobs",
            data={"language": "es"},
            files={"video": ("documento.txt", b"contenido", "text/plain")},
        )
        assert response.status_code == 400
        assert "Formato no soportado" in response.json()["detail"]

    def test_archivo_demasiado_grande_retorna_413(self, monkeypatch):
        monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)
        response = client.post(
            "/jobs",
            data={"language": "es"},
            files={"video": ("video.mp4", b"x" * (1024 * 1024 + 1), "video/mp4")},
        )
        assert response.status_code == 413
        assert "límite" in response.json()["detail"]

    def test_video_ilegible_retorna_400(self, monkeypatch):
        def fake_duracion(path):
            raise RuntimeError("no es un vídeo válido")

        monkeypatch.setattr(job_service, "obtener_duracion", fake_duracion)
        response = client.post(
            "/jobs",
            data={"language": "es"},
            files={"video": ("video.mp4", b"contenido", "video/mp4")},
        )
        assert response.status_code == 400
        assert "No se pudo leer el vídeo" in response.json()["detail"]

    def test_duracion_excedida_retorna_400(self, monkeypatch):
        monkeypatch.setattr(job_service, "obtener_duracion", lambda path: 999999.0)
        monkeypatch.setattr(settings, "MAX_DURATION_SECONDS", 10)
        response = client.post(
            "/jobs",
            data={"language": "es"},
            files={"video": ("video.mp4", b"contenido", "video/mp4")},
        )
        assert response.status_code == 400
        assert "duración" in response.json()["detail"]


class TestLogging:
    def test_logger_configurado_con_handler(self):
        logger = get_logger("test")
        assert logger.name == "subtitulator.test"
        root = logging.getLogger("subtitulator")
        assert root.handlers
        assert root.level == logging.INFO

    def test_mark_error_loguea(self, caplog):
        from app.repositories import job_repository
        from app.database import get_connection, init_db

        init_db()
        with get_connection() as connection:
            connection.execute("DELETE FROM jobs WHERE id = 'fase5_log'")
        job_repository.create(
            {
                "id": "fase5_log",
                "original_filename": "v.mp4",
                "input_path": "data/jobs/fase5_log/input.mp4",
                "language": "es",
                "model": "small",
            }
        )
        subtit_logger = logging.getLogger("subtitulator")
        subtit_logger.addHandler(caplog.handler)
        try:
            with caplog.at_level(logging.ERROR, logger="subtitulator"):
                job_service._mark_error("fase5_log", "fallo de prueba")
        finally:
            subtit_logger.removeHandler(caplog.handler)
        assert any("fallo de prueba" in record.message for record in caplog.records)


class TestManejadorGlobal:
    def test_excepcion_inesperada_retorna_500_limpio(self, monkeypatch):
        monkeypatch.setattr(
            job_service,
            "list_jobs",
            lambda: (_ for _ in ()).throw(RuntimeError("boom interno")),
        )
        safe_client = TestClient(app, raise_server_exceptions=False)
        response = safe_client.get("/jobs")
        assert response.status_code == 500
        assert response.json()["detail"] == "Error interno del servidor"
        assert "boom interno" not in response.text
