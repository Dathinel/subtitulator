import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
import os


client = TestClient(app)


class TestHealthcheck:
    def test_healthcheck_retorna_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_healthcheck_retorna_json(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_healthcheck_contiene_nombre_y_version(self):
        response = client.get("/health")
        data = response.json()
        assert data["app"] == settings.APP_NAME
        assert data["version"] == settings.APP_VERSION


class TestConfig:
    def test_app_name(self):
        assert settings.APP_NAME == "Subtitulator"

    def test_app_version(self):
        assert settings.APP_VERSION == "0.1.0"

    def test_whisper_model_por_defecto(self):
        assert settings.WHISPER_MODEL == "small"

    def test_whisper_device_cpu(self):
        assert settings.WHISPER_DEVICE == "cpu"

    def test_compute_type_int8(self):
        assert settings.WHISPER_COMPUTE_TYPE == "int8"

    def test_max_file_size(self):
        assert settings.MAX_FILE_SIZE_MB == 500

    def test_max_duration(self):
        assert settings.MAX_DURATION_SECONDS == 3600

    def test_extensiones_permitidas(self):
        assert ".mp4" in settings.ALLOWED_EXTENSIONS
        assert ".mov" in settings.ALLOWED_EXTENSIONS
        assert ".mkv" in settings.ALLOWED_EXTENSIONS
        assert ".avi" in settings.ALLOWED_EXTENSIONS
        assert ".webm" in settings.ALLOWED_EXTENSIONS
        assert len(settings.ALLOWED_EXTENSIONS) == 5

    def test_directorios_creados(self):
        assert os.path.isdir(settings.MODEL_DIR)
        assert os.path.isdir(settings.DATA_DIR)
        assert os.path.isdir(settings.JOBS_DIR)
        assert os.path.isdir(settings.TEMP_DIR)


class TestCORS:
    def test_cors_headers_presentes(self):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in (200, 405)


class TestEstructuraArchivos:
    def test_init_app_existe(self):
        assert os.path.isfile(os.path.join("app", "__init__.py"))

    def test_init_services_existe(self):
        assert os.path.isfile(os.path.join("app", "services", "__init__.py"))

    def test_main_py_existe(self):
        assert os.path.isfile(os.path.join("app", "main.py"))

    def test_config_py_existe(self):
        assert os.path.isfile(os.path.join("app", "config.py"))

    def test_requirements_txt_existe(self):
        assert os.path.isfile("requirements.txt")

    def test_dockerfile_existe(self):
        assert os.path.isfile("Dockerfile")
