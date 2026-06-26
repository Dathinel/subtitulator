# Plan de Proyecto — Subtitulator

> Documento de referencia central. Cualquier persona o agente que intervenga en el
> proyecto debe leer este documento primero. Los detalles específicos para agentes de
> IA están en `AGENTS.md` y `CLAUDE.md`.

---

## 1. Objetivo

Crear una **aplicación web** que añada subtítulos a vídeos que no los tienen,
**transcribiendo el audio** del propio vídeo (no analizando los frames) y **quemando**
los subtítulos sobre la imagen.

Características clave acordadas:

- **Transcripción del audio** (voz → texto con marcas de tiempo).
- **Mismo idioma** de entrada y salida, con **selección del idioma** (soporte multi-idioma).
- **Subtítulos quemados** en el vídeo (siempre visibles, no pista opcional).
- **Paso de revisión/edición** del texto y los tiempos antes de renderizar.
- **Personalización básica** del estilo de los subtítulos (fuente, tamaño, color, borde, posición).
- **Procesamiento en segundo plano** con seguimiento de progreso (polling).
- **Historial** de trabajos persistido.

### Decisión de arquitectura: automatización, NO agente

El núcleo es un **pipeline determinista**, no un agente de IA. La transcripción
proviene del **audio**, por lo que herramientas especializadas (Whisper + FFmpeg)
resuelven el problema de forma robusta, rápida y predecible. Un agente que "analice
frames" sería lento, caro y no aportaría nada al objetivo. La IA aquí se limita al
modelo de transcripción (Whisper) usado como función, sin bucle de decisión agéntico.

---

## 2. Stack tecnológico

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Backend | **Python 3.11 + FastAPI** | API async, tareas en segundo plano |
| Transcripción | **faster-whisper** (local) | Modelo `small` por defecto, configurable; CPU `int8` |
| Procesado A/V | **FFmpeg** | Extraer audio + quemar subtítulos (filtro ASS) |
| Subtítulos | Formato **ASS** | Permite personalización avanzada futura sin reescritura |
| Base de datos | **SQLite** | Historial de trabajos |
| Frontend | **React + Vite + TypeScript + Tailwind** | Diseño visual con skills `/ui-ux-pro-max` y `/frontend-design` |
| Despliegue | **Docker + docker-compose** | CPU por defecto; modelos y datos en volúmenes |

### Modelos de transcripción (faster-whisper, gratuitos)

`small` por defecto (≈466 MB, ~2 GB RAM, buena calidad, práctico en CPU). Configurable
a `base`/`medium` si un vídeo concreto lo requiere. Ejecución en **CPU** (`device=cpu`,
`compute_type=int8`) porque el entorno objetivo tiene GPU integrada (sin CUDA).

---

## 3. Componentes a crear

### Backend (`/backend`)

- **API REST (FastAPI)**
  - `POST /jobs` — subir vídeo + idioma + modelo → valida → crea job → devuelve `job_id`.
  - `GET /jobs/{id}` — estado y progreso del trabajo.
  - `GET /jobs/{id}/transcript` — segmentos transcritos (para editar).
  - `PUT /jobs/{id}/transcript` — guardar transcripción editada por el usuario.
  - `POST /jobs/{id}/render` — confirmar y quemar subtítulos con opciones de estilo.
  - `GET /jobs/{id}/download` — descargar vídeo subtitulado.
  - `GET /jobs` — historial.
- **Servicios**
  - `audio_service` — extracción de audio con FFmpeg.
  - `transcription_service` — faster-whisper, segmentos con timestamps.
  - `subtitle_service` — generación de archivo `.ass` desde segmentos + estilo.
  - `render_service` — quemado de subtítulos con FFmpeg.
  - `job_service` — orquestación del pipeline en segundo plano + estados.
- **Persistencia** — modelo `Job` en SQLite (id, archivo, idioma, modelo, estado, rutas, fechas).
- **Validación** — formatos (`mp4`, `mov`, `mkv`, `avi`, `webm`), tamaño máx. y duración máx. configurables.

### Frontend (`/frontend`)

- Pantalla de **subida** (vídeo + selección de idioma y modelo).
- Pantalla de **progreso** (polling del estado del job).
- **Editor de subtítulos** (texto + tiempos por segmento).
- Panel de **estilo básico** (fuente, tamaño, color, color de borde, posición).
- Pantalla de **descarga** + **historial**.
- *(Diseño visual concreto se define con las skills de frontend.)*

### Infraestructura

- `Dockerfile` backend (python:3.11-slim + FFmpeg vía apt).
- `Dockerfile` frontend (build Vite + servir estático).
- `docker-compose.yml` (backend + frontend + volúmenes de modelos y datos).

---

## 4. Flujo de datos

1. Usuario sube vídeo, elige **idioma** y **modelo** → backend valida → crea `Job` (`pending`) → responde `job_id`.
2. Tarea en segundo plano: `processing` → **extraer audio** (FFmpeg) → **transcribir** (faster-whisper) → `transcribed`.
3. Frontend hace **polling** de `GET /jobs/{id}` para mostrar progreso.
4. Usuario **revisa/edita** la transcripción (texto y tiempos) → guarda.
5. Usuario ajusta **estilo** y confirma → `rendering` → **quemar subtítulos** (FFmpeg) → `done`.
6. Usuario **descarga** el vídeo. El trabajo queda en el **historial**.

Estados del job: `pending → processing → transcribed → rendering → done` (o `error` en cualquier punto).

---

## 5. Manejo de errores

| Situación | Manejo |
|-----------|--------|
| Formato no soportado | Rechazo en validación con mensaje claro (HTTP 400). |
| Archivo demasiado grande / largo | Rechazo con límite indicado (HTTP 413/400). |
| Vídeo sin pista de audio | Error controlado en `audio_service`; job → `error` con detalle. |
| Fallo de FFmpeg | Capturar stderr, registrar log, job → `error`, no romper el servidor. |
| Fallo/transcripción vacía | Marcar `error`, permitir reintento. |
| Job inexistente | HTTP 404. |
| Excepción inesperada en background | Try/except global por job; estado `error` + mensaje; el resto de jobs sigue. |
| Limpieza | Borrar archivos temporales (audio extraído) al finalizar o fallar. |

Principio: **un job que falla nunca tumba el servidor ni afecta a otros jobs**. Todo
error queda persistido en el job con un mensaje legible para el frontend.

---

## 6. Fases de implementación

> Las fases se ejecutan en orden y de forma continua (no se pide permiso entre fases).

### Fase 1 — Estructura y entorno
- Estructura de carpetas (`backend/`, `frontend/`), `requirements.txt`, configuración.
- Dockerfile backend + docker-compose base con volúmenes.
- Esqueleto FastAPI con healthcheck.

### Fase 2 — Pipeline de transcripción (núcleo)
- `audio_service` (extracción FFmpeg).
- `transcription_service` (faster-whisper, modelo `small`, segmentos con tiempos).
- Prueba end-to-end por CLI: vídeo → segmentos.

### Fase 3 — Persistencia y jobs en segundo plano
- Modelo `Job` en SQLite + repositorio.
- `job_service` con estados y ejecución en background (FastAPI BackgroundTasks).
- Endpoints `POST /jobs`, `GET /jobs/{id}`, `GET /jobs`.

### Fase 4 — Subtítulos y renderizado
- `subtitle_service` (generación `.ass` con estilo básico).
- `render_service` (quemado con FFmpeg).
- Endpoints `PUT /jobs/{id}/transcript`, `POST /jobs/{id}/render`, `GET /jobs/{id}/download`.

### Fase 5 — Validación y manejo de errores
- Validación de formato/tamaño/duración configurable.
- Manejo de errores robusto y limpieza de temporales.
- Logs.

### Fase 6 — Frontend
- App React + Vite + TS + Tailwind.
- Pantallas: subida, progreso (polling), editor, estilo, descarga, historial.
- Diseño visual con skills `/ui-ux-pro-max` y `/frontend-design`.
- Dockerfile frontend + integración en compose.

### Fase 7 — Integración y pulido
- Pruebas end-to-end del flujo completo en Docker.
- Ajuste de límites, mensajes de error y experiencia.

---

## 7. Extensibilidad reservada (YAGNI)

- **Personalización avanzada de subtítulos** (sombra, fondo, animaciones, karaoke por
  palabra): el uso de **ASS** desde el inicio permite añadirla sin reescribir el pipeline.
- **GPU/CUDA**: cambiar a imagen base CUDA + `device=cuda` si en el futuro hay GPU NVIDIA.
- **Traducción**: el pipeline puede ampliarse con un paso de traducción si se decide.

No se implementan ahora para no añadir complejidad innecesaria.
