import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Subtitulator"
    APP_VERSION: str = "0.1.0"

    MODEL_DIR: str = str(Path(__file__).parent.parent / "models")
    DATA_DIR: str = str(Path(__file__).parent.parent / "data")
    JOBS_DIR: str = str(Path(DATA_DIR) / "jobs")
    TEMP_DIR: str = str(Path(DATA_DIR) / "temp")

    WHISPER_MODEL: str = "small"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    MAX_FILE_SIZE_MB: int = 500
    MAX_DURATION_SECONDS: int = 3600
    ALLOWED_EXTENSIONS: set = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(DATA_DIR, 'subtitulator.db')}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()

os.makedirs(settings.MODEL_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.JOBS_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
