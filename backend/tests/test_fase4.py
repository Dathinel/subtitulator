import os
import subprocess

from fastapi.testclient import TestClient

from app.config import settings
from app.database import get_connection, init_db
from app.main import app
from app.repositories import job_repository
from app.schemas import JobStatus, SubtitleStyle
from app.services import job_service
from app.services.render_service import quemar_subtitulos
from app.services.subtitle_service import generar_ass


client = TestClient(app)


def limpiar_jobs():
    init_db()
    with get_connection() as connection:
        connection.execute("DELETE FROM jobs WHERE id LIKE 'fase4_%'")


def crear_job_transcrito(job_id: str, tmp_path):
    job_dir = tmp_path / job_id
    job_dir.mkdir()
    input_path = job_dir / "input.mp4"
    transcript_path = job_dir / "transcript.json"
    input_path.write_bytes(b"video")
    transcript_path.write_text(
        '{"segmentos":[{"inicio":0.0,"fin":1.5,"texto":"Hola mundo"}]}',
        encoding="utf-8",
    )
    job_repository.create(
        {
            "id": job_id,
            "original_filename": "video.mp4",
            "input_path": str(input_path),
            "language": "es",
            "model": "small",
            "status": JobStatus.transcribed.value,
            "progress": 100,
            "transcript_path": str(transcript_path),
        }
    )
    return input_path, transcript_path


class TestSubtitleService:
    def test_generar_ass_crea_archivo_con_estilo_y_dialogos(self, tmp_path):
        output_path = tmp_path / "subtitles.ass"
        style = SubtitleStyle(
            font="Arial",
            font_size=42,
            color="#FFFFFF",
            outline_color="#000000",
            position="bottom",
        )

        generar_ass(
            [{"inicio": 0.0, "fin": 2.25, "texto": "Hola mundo"}],
            style,
            str(output_path),
        )

        contenido = output_path.read_text(encoding="utf-8")
        assert "[Script Info]" in contenido
        assert "Style: Default,Arial,42" in contenido
        assert "Dialogue: 0,0:00:00.00,0:00:02.25" in contenido
        assert "Hola mundo" in contenido

    def test_generar_ass_rechaza_segmentos_vacios(self, tmp_path):
        output_path = tmp_path / "subtitles.ass"

        try:
            generar_ass([], SubtitleStyle(), str(output_path))
        except Exception as exc:
            assert "No hay segmentos" in str(exc)
        else:
            raise AssertionError("Se esperaba un error con segmentos vacíos")


class TestTranscriptEndpoints:
    def test_get_transcript_retorna_segmentos(self, tmp_path):
        limpiar_jobs()
        crear_job_transcrito("fase4_get_transcript", tmp_path)

        response = client.get("/jobs/fase4_get_transcript/transcript")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "fase4_get_transcript"
        assert data["segmentos"][0]["texto"] == "Hola mundo"

    def test_put_transcript_guarda_edicion(self, tmp_path):
        limpiar_jobs()
        crear_job_transcrito("fase4_put_transcript", tmp_path)

        response = client.put(
            "/jobs/fase4_put_transcript/transcript",
            json={"segmentos": [{"inicio": 0.0, "fin": 1.2, "texto": "Texto editado"}]},
        )

        assert response.status_code == 200
        assert response.json()["segmentos"][0]["texto"] == "Texto editado"

        transcript = client.get("/jobs/fase4_put_transcript/transcript").json()
        assert transcript["segmentos"][0]["texto"] == "Texto editado"

    def test_put_transcript_valida_tiempos(self, tmp_path):
        limpiar_jobs()
        crear_job_transcrito("fase4_put_invalid", tmp_path)

        response = client.put(
            "/jobs/fase4_put_invalid/transcript",
            json={"segmentos": [{"inicio": 2.0, "fin": 1.0, "texto": "Mal"}]},
        )

        assert response.status_code == 422


class TestRenderEndpoints:
    def test_post_render_genera_video_y_estado_done(self, monkeypatch, tmp_path):
        limpiar_jobs()
        crear_job_transcrito("fase4_render", tmp_path)

        def fake_render(video_path: str, subtitles_path: str, output_path: str):
            with open(output_path, "wb") as file:
                file.write(b"video renderizado")
            return output_path

        monkeypatch.setattr(job_service, "quemar_subtitulos", fake_render)

        response = client.post(
            "/jobs/fase4_render/render",
            json={
                "font": "Arial",
                "font_size": 40,
                "color": "#FFFFFF",
                "outline_color": "#000000",
                "position": "bottom",
            },
        )

        assert response.status_code == 200
        job = job_repository.get("fase4_render")
        assert job["status"] == JobStatus.done.value
        assert os.path.isfile(job["subtitles_path"])
        assert os.path.isfile(job["output_path"])

    def test_download_retorna_video_renderizado(self, monkeypatch, tmp_path):
        limpiar_jobs()
        crear_job_transcrito("fase4_download", tmp_path)

        def fake_render(video_path: str, subtitles_path: str, output_path: str):
            with open(output_path, "wb") as file:
                file.write(b"video renderizado")
            return output_path

        monkeypatch.setattr(job_service, "quemar_subtitulos", fake_render)
        client.post("/jobs/fase4_download/render", json={})

        response = client.get("/jobs/fase4_download/download")

        assert response.status_code == 200
        assert response.content == b"video renderizado"

    def test_render_job_sin_transcripcion_retorna_409(self, tmp_path):
        limpiar_jobs()
        input_path = tmp_path / "input.mp4"
        input_path.write_bytes(b"video")
        job_repository.create(
            {
                "id": "fase4_no_transcrito",
                "original_filename": "video.mp4",
                "input_path": str(input_path),
                "language": "es",
                "model": "small",
            }
        )

        response = client.post("/jobs/fase4_no_transcrito/render", json={})

        assert response.status_code == 409


class TestRenderServiceReal:
    def test_quemar_subtitulos_con_ffmpeg_real(self, tmp_path):
        video_path = tmp_path / "input.mp4"
        subtitles_path = tmp_path / "subtitles.ass"
        output_path = tmp_path / "output.mp4"
        cmd = [
            settings.FFMPEG_PATH,
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x240:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            "-y",
            str(video_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        generar_ass(
            [{"inicio": 0.0, "fin": 0.8, "texto": "Hola"}],
            SubtitleStyle(),
            str(subtitles_path),
        )

        quemar_subtitulos(str(video_path), str(subtitles_path), str(output_path))

        assert output_path.is_file()
        assert output_path.stat().st_size > 0
