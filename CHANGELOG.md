# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y el proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [0.1.0] - 2026-06-26

### Añadido
- Pipeline de transcripción local con `faster-whisper` (modelo `small`, CPU `int8`).
- Extracción de audio y quemado de subtítulos con FFmpeg (formato ASS).
- API FastAPI con tareas en segundo plano y seguimiento de estado por *polling*.
- Persistencia de trabajos en SQLite e historial.
- Validación de entrada (formato, tamaño y duración) y manejo de errores con logging.
- Frontend React + Vite + TypeScript + Tailwind: subida, progreso, editor de
  transcripción, panel de estilo con vista previa, descarga e historial.
- Despliegue con Docker Compose (backend + frontend).
- Suite de tests: 57 en backend (pytest) y 12 en frontend (Vitest).
