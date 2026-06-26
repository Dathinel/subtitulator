# AGENTS.md — Guía para agentes de IA (Subtitulator)

> Documento específico para agentes que trabajen en este proyecto. La visión y el plan
> general están en `plan.md` (documento de referencia central) — léelo primero.
> `CLAUDE.md` complementa este archivo con notas específicas para Claude Code.

---

## Principio rector

Este proyecto es una **automatización determinista**, NO un sistema agéntico. No
introduzcas agentes, bucles de decisión LLM ni análisis de frames para generar los
subtítulos. Los subtítulos provienen del **audio** (Whisper). La IA se usa únicamente
como modelo de transcripción invocado como función.

---

## Reglas de trabajo

- **No pidas permiso entre fases.** Implementa de forma continua hasta completar el
  objetivo de cada fase descrita en `plan.md`.
- **Respeta YAGNI.** No añadas features fuera del alcance acordado. La personalización
  avanzada de subtítulos y la traducción están explícitamente reservadas para el futuro.
- **No rompas el contrato del pipeline.** Estados del job:
  `pending → processing → transcribed → rendering → done` (o `error`).
- **Un job que falla nunca debe tumbar el servidor** ni afectar a otros jobs. Captura
  errores por job y persístelos con un mensaje legible.
- **Limpia los temporales** (audio extraído, archivos intermedios) al terminar o fallar.

---

## Stack y decisiones cerradas

- Backend: **Python 3.11 + FastAPI**, tareas en segundo plano (BackgroundTasks) + polling.
- Transcripción: **faster-whisper** local, modelo **`small`** por defecto (configurable),
  `device=cpu`, `compute_type=int8`. Sin API externa.
- A/V: **FFmpeg** (extraer audio y quemar subtítulos).
- Subtítulos: formato **ASS** (no SRT plano) para permitir personalización avanzada futura.
- BD: **SQLite** (historial de trabajos).
- Frontend: **React + Vite + TypeScript + Tailwind**.
- Despliegue: **Docker + docker-compose**, CPU por defecto, modelos y datos en volúmenes.

---

## Frontend — skills obligatorias

Para crear e implementar el frontend, usa **siempre** las skills:

- `/ui-ux-pro-max`
- `/frontend-design`

El **diseño visual concreto** se define con esas skills; el stack ya está fijado arriba.

---

## Convenciones

- Estructura: `backend/` y `frontend/` separados; servicios del backend con
  responsabilidad única (`audio_service`, `transcription_service`, `subtitle_service`,
  `render_service`, `job_service`).
- Configuración por variables de entorno (modelo Whisper, límites de tamaño/duración,
  formatos permitidos, rutas de volúmenes).
- Modelos no horneados en la imagen Docker: se descargan a un **volumen** persistente.
- Mensajes de error siempre legibles para el frontend (no exponer trazas crudas).

---

## Idioma

Toda la comunicación, comentarios y documentación en **español** (con tildes y signos
correctos). Los identificadores de código en su forma original (inglés técnico).
