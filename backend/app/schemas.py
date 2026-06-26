from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    transcribed = "transcribed"
    rendering = "rendering"
    done = "done"
    error = "error"


class JobResponse(BaseModel):
    id: str
    original_filename: str
    language: str | None
    model: str
    status: JobStatus
    progress: int
    error_message: str | None = None
    created_at: str
    updated_at: str


class TranscriptSegment(BaseModel):
    inicio: float = Field(ge=0)
    fin: float = Field(gt=0)
    texto: str = Field(min_length=1)

    @field_validator("texto")
    @classmethod
    def limpiar_texto(cls, value: str) -> str:
        return value.strip()


class TranscriptPayload(BaseModel):
    segmentos: list[TranscriptSegment]

    @field_validator("segmentos")
    @classmethod
    def validar_segmentos(cls, value: list[TranscriptSegment]) -> list[TranscriptSegment]:
        for segment in value:
            if segment.inicio >= segment.fin:
                raise ValueError("Cada segmento debe tener inicio menor que fin")
        return value


class TranscriptResponse(BaseModel):
    job_id: str
    segmentos: list[TranscriptSegment]


class SubtitleStyle(BaseModel):
    font: str = Field(default="Arial", min_length=1, max_length=80)
    font_size: int = Field(default=48, ge=12, le=120)
    color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    outline_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    position: Literal["top", "middle", "bottom"] = "bottom"
