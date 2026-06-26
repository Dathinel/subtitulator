import os

from fastapi.testclient import TestClient

from app.database import get_connection, init_db
from app.main import app
from app.repositories import job_repository
from app.schemas import JobStatus
from app.services import job_service


client = TestClient(app)


def limpiar_jobs():
    init_db()
    with get_connection() as connection:
        connection.execute("DELETE FROM jobs WHERE id LIKE 'fase3_%'")


class TestPersistenciaJobs:
    def test_crear_y_obtener_job_en_sqlite(self):
        limpiar_jobs()
        job = job_repository.create(
            {
                "id": "fase3_repo",
                "original_filename": "video.mp4",
                "input_path": "data/jobs/fase3_repo/input.mp4",
                "language": "es",
                "model": "small",
            }
        )

        guardado = job_repository.get(job["id"])

        assert guardado is not None
        assert guardado["status"] == JobStatus.pending.value
        assert guardado["progress"] == 0
        assert guardado["language"] == "es"

    def test_actualizar_estado_y_progreso(self):
        limpiar_jobs()
        job_repository.create(
            {
                "id": "fase3_update",
                "original_filename": "video.mp4",
                "input_path": "data/jobs/fase3_update/input.mp4",
                "language": None,
                "model": "small",
            }
        )

        actualizado = job_repository.update(
            "fase3_update",
            status=JobStatus.processing.value,
            progress=40,
        )

        assert actualizado["status"] == JobStatus.processing.value
        assert actualizado["progress"] == 40

    def test_listar_jobs(self):
        limpiar_jobs()
        job_repository.create(
            {
                "id": "fase3_list",
                "original_filename": "video.mp4",
                "input_path": "data/jobs/fase3_list/input.mp4",
                "language": "en",
                "model": "small",
            }
        )

        jobs = job_repository.list()

        assert any(job["id"] == "fase3_list" for job in jobs)


class TestEndpointsJobs:
    def test_post_jobs_crea_job_y_lanza_background(self, monkeypatch):
        limpiar_jobs()

        monkeypatch.setattr(job_service, "obtener_duracion", lambda path: 5.0)
        monkeypatch.setattr(job_service.uuid, "uuid4", lambda: type("UUID", (), {"hex": "fase3_post_job"})())

        def fake_process(job_id: str):
            job_repository.update(job_id, status=JobStatus.transcribed.value, progress=100)

        monkeypatch.setattr(job_service, "process_transcription", fake_process)

        response = client.post(
            "/jobs",
            data={"language": "es", "model": "small"},
            files={"video": ("video.mp4", b"contenido", "video/mp4")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "video.mp4"
        assert data["language"] == "es"
        assert data["model"] == "small"

        status_response = client.get(f"/jobs/{data['id']}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == JobStatus.transcribed.value

    def test_get_jobs_retorna_historial(self):
        limpiar_jobs()
        job_repository.create(
            {
                "id": "fase3_historial",
                "original_filename": "video.mp4",
                "input_path": "data/jobs/fase3_historial/input.mp4",
                "language": "es",
                "model": "small",
            }
        )

        response = client.get("/jobs")

        assert response.status_code == 200
        assert any(job["id"] == "fase3_historial" for job in response.json())

    def test_get_job_inexistente_retorna_404(self):
        limpiar_jobs()

        response = client.get("/jobs/no_existe")

        assert response.status_code == 404


class TestBackgroundTranscription:
    def test_process_transcription_marca_transcribed_y_guarda_transcript(self, monkeypatch, tmp_path):
        limpiar_jobs()
        video_path = tmp_path / "input.mp4"
        audio_path = tmp_path / "audio.wav"
        video_path.write_bytes(b"video")
        audio_path.write_bytes(b"audio")

        job_repository.create(
            {
                "id": "fase3_background",
                "original_filename": "video.mp4",
                "input_path": str(video_path),
                "language": "es",
                "model": "small",
            }
        )
        monkeypatch.setattr(job_service, "extraer_audio", lambda path: str(audio_path))
        monkeypatch.setattr(
            job_service,
            "transcribir",
            lambda path, language: [{"inicio": 0.0, "fin": 1.0, "texto": "Hola"}],
        )

        job_service.process_transcription("fase3_background")

        job = job_repository.get("fase3_background")
        assert job["status"] == JobStatus.transcribed.value
        assert job["progress"] == 100
        assert os.path.isfile(job["transcript_path"])
        assert not audio_path.exists()

    def test_process_transcription_marca_error_sin_tumbar_servidor(self, monkeypatch, tmp_path):
        limpiar_jobs()
        video_path = tmp_path / "input.mp4"
        video_path.write_bytes(b"video")
        job_repository.create(
            {
                "id": "fase3_error",
                "original_filename": "video.mp4",
                "input_path": str(video_path),
                "language": "es",
                "model": "small",
            }
        )
        monkeypatch.setattr(job_service, "extraer_audio", lambda path: (_ for _ in ()).throw(RuntimeError("fallo controlado")))

        job_service.process_transcription("fase3_error")

        job = job_repository.get("fase3_error")
        assert job["status"] == JobStatus.error.value
        assert "fallo controlado" in job["error_message"]
