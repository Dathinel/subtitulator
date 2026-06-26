# CLAUDE.md — Guía para Claude Code (Subtitulator)

> Notas específicas para Claude Code. Complementa `AGENTS.md`. La referencia central del
> proyecto es `plan.md` — léelo antes de empezar cualquier tarea.

---

## Qué es este proyecto

Aplicación web que añade **subtítulos quemados** a vídeos sin subtítulos,
**transcribiendo el audio** (mismo idioma, seleccionable) con un paso de **revisión**
antes de renderizar. Es una **automatización determinista** (Whisper + FFmpeg), NO un
agente. Detalles completos en `plan.md`.

---

## Decisiones que NO debes cambiar

- Automatización determinista, no agente. No analices frames para generar subtítulos.
- `faster-whisper` **local**, modelo `small` por defecto, **CPU** `int8`. Sin APIs de pago.
- Subtítulos en formato **ASS**.
- BD **SQLite**. Backend **FastAPI**. Frontend **React + Vite + TS + Tailwind**.
- Despliegue en **Docker Compose**; modelos y datos en **volúmenes** (no en la imagen).

---

## Flujo de trabajo esperado

- Sigue las **fases de `plan.md`** en orden y **sin pedir permiso entre fases**.
- Aplica **YAGNI**: no añadas la personalización avanzada de subtítulos ni traducción
  (están reservadas para más adelante).
- Para el **frontend**, invoca siempre las skills `/ui-ux-pro-max` y `/frontend-design`.

---

## Comandos útiles (se completarán durante la implementación)

```bash
# Backend (desarrollo local)
cd backend && uvicorn app.main:app --reload

# Docker
docker-compose up --build

# Frontend (desarrollo local)
cd frontend && npm run dev
```

---

## Manejo de errores (recordatorio)

- Un job que falla → estado `error` con mensaje legible; nunca tumbar el servidor.
- Capturar y registrar el `stderr` de FFmpeg.
- Validar formato/tamaño/duración antes de procesar.
- Limpiar archivos temporales al terminar o fallar.

---

## Idioma

Responde y documenta en **español** con ortografía correcta (tildes incluidas).
Identificadores de código en inglés técnico.
