from sqlite3 import Row

from app.database import get_connection, utc_now


def _row_to_dict(row: Row | None) -> dict | None:
    return dict(row) if row else None


class JobRepository:
    def create(self, job: dict) -> dict:
        now = utc_now()
        payload = {
            **job,
            "status": job.get("status", "pending"),
            "progress": job.get("progress", 0),
            "error_message": job.get("error_message"),
            "output_path": job.get("output_path"),
            "transcript_path": job.get("transcript_path"),
            "subtitles_path": job.get("subtitles_path"),
            "created_at": now,
            "updated_at": now,
        }
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    id, original_filename, input_path, output_path, transcript_path,
                    subtitles_path, language, model, status, progress, error_message,
                    created_at, updated_at
                )
                VALUES (
                    :id, :original_filename, :input_path, :output_path, :transcript_path,
                    :subtitles_path, :language, :model, :status, :progress, :error_message,
                    :created_at, :updated_at
                )
                """,
                payload,
            )
        return payload

    def get(self, job_id: str) -> dict | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list(self) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def update(self, job_id: str, **fields) -> dict | None:
        if not fields:
            return self.get(job_id)

        fields["updated_at"] = utc_now()
        assignments = ", ".join(f"{key} = :{key}" for key in fields)
        payload = {**fields, "id": job_id}

        with get_connection() as connection:
            connection.execute(
                f"UPDATE jobs SET {assignments} WHERE id = :id",
                payload,
            )
        return self.get(job_id)


job_repository = JobRepository()
