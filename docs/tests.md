# Reporte de Tests — Subtitulator

## Fase 1 — Estructura y entorno

**Fecha**: 25/06/2026
**Resultado**: 19/19 tests aprobados

| Test | Resultado |
|------|-----------|
| `test_healthcheck_retorna_200` | APROBADO |
| `test_healthcheck_retorna_json` | APROBADO |
| `test_healthcheck_contiene_nombre_y_version` | APROBADO |
| `test_app_name` | APROBADO |
| `test_app_version` | APROBADO |
| `test_whisper_model_por_defecto` | APROBADO |
| `test_whisper_device_cpu` | APROBADO |
| `test_compute_type_int8` | APROBADO |
| `test_max_file_size` | APROBADO |
| `test_max_duration` | APROBADO |
| `test_extensiones_permitidas` | APROBADO |
| `test_directorios_creados` | APROBADO |
| `test_cors_headers_presentes` | APROBADO |
| `test_init_app_existe` | APROBADO |
| `test_init_services_existe` | APROBADO |
| `test_main_py_existe` | APROBADO |
| `test_config_py_existe` | APROBADO |
| `test_requirements_txt_existe` | APROBADO |
| `test_dockerfile_existe` | APROBADO |

### Resumen Fase 1
- Estructura de carpetas creada: `backend/`, `backend/app/`, `backend/app/services/`, `backend/tests/`, `frontend/`.
- `requirements.txt` con dependencias del backend.
- Configuración centralizada con `pydantic-settings` y variables de entorno.
- Esqueleto FastAPI con endpoint `/health` funcional.
- CORS habilitado para desarrollo.
- `Dockerfile` del backend con Python 3.11-slim + FFmpeg.
- `docker-compose.yml` con servicio backend y volúmenes para modelos y datos.
- Directorios `models/`, `data/`, `data/jobs/`, `data/temp/` creados automáticamente.

---

## Fase 2 — Pipeline de transcripción núcleo

**Fecha**: 25/06/2026
**Resultado**: 11/11 tests aprobados

| Test | Resultado |
|------|-----------|
| `test_extraer_audio_exitoso` | APROBADO |
| `test_extraer_audio_archivo_inexistente` | APROBADO |
| `test_extraer_audio_video_sin_audio` | APROBADO |
| `test_obtener_duracion` | APROBADO |
| `test_obtener_duracion_archivo_inexistente` | APROBADO |
| `test_extraer_audio_tiene_formato_correcto` | APROBADO |
| `test_transcribir_archivo_inexistente` | APROBADO |
| `test_transcribir_audio_con_tono` | APROBADO |
| `test_estructura_segmentos` | APROBADO |
| `test_pipeline_completo` | APROBADO |
| `test_limpieza_temporales` | APROBADO |

### Resumen Fase 2
- `audio_service.py`: extracción de audio con FFmpeg, WAV 16 kHz mono, detección de pista de audio vía ffprobe y cálculo de duración.
- Manejo de errores de audio con `NoAudioTrackError` y `AudioExtractionError`.
- `transcription_service.py`: transcripción con `faster-whisper`, modelo `small`, CPU `int8`.
- Segmentos con timestamps en formato `inicio`, `fin`, `texto`.
- `transcribe.py`: script CLI para prueba end-to-end.
- Pipeline validado: vídeo con audio → extracción → transcripción → segmentos.

---

## Fase 3 — Persistencia y jobs en segundo plano

**Fecha**: 25/06/2026
**Resultado**: 8/8 tests aprobados

| Test | Resultado |
|------|-----------|
| `test_crear_y_obtener_job_en_sqlite` | APROBADO |
| `test_actualizar_estado_y_progreso` | APROBADO |
| `test_listar_jobs` | APROBADO |
| `test_post_jobs_crea_job_y_lanza_background` | APROBADO |
| `test_get_jobs_retorna_historial` | APROBADO |
| `test_get_job_inexistente_retorna_404` | APROBADO |
| `test_process_transcription_marca_transcribed_y_guarda_transcript` | APROBADO |
| `test_process_transcription_marca_error_sin_tumbar_servidor` | APROBADO |

### Resumen Fase 3
- Persistencia SQLite inicializada con tabla `jobs`.
- Repositorio `JobRepository` para crear, consultar, listar y actualizar jobs.
- Endpoints añadidos: `POST /jobs`, `GET /jobs/{id}` y `GET /jobs`.
- `job_service.py` orquesta la transcripción en segundo plano con `BackgroundTasks`.
- Estados aplicados según contrato: `pending`, `processing`, `transcribed` y `error`.
- Errores de transcripción capturados por job sin tumbar el servidor.
- Limpieza del audio temporal al terminar o fallar el procesamiento.

---

## Fase 4 — Subtítulos y renderizado

**Fecha**: 25/06/2026
**Resultado**: 9/9 tests aprobados

| Test | Resultado |
|------|-----------|
| `test_generar_ass_crea_archivo_con_estilo_y_dialogos` | APROBADO |
| `test_generar_ass_rechaza_segmentos_vacios` | APROBADO |
| `test_get_transcript_retorna_segmentos` | APROBADO |
| `test_put_transcript_guarda_edicion` | APROBADO |
| `test_put_transcript_valida_tiempos` | APROBADO |
| `test_post_render_genera_video_y_estado_done` | APROBADO |
| `test_download_retorna_video_renderizado` | APROBADO |
| `test_render_job_sin_transcripcion_retorna_409` | APROBADO |
| `test_quemar_subtitulos_con_ffmpeg_real` | APROBADO |

### Resumen Fase 4
- `subtitle_service.py`: generación de subtítulos `.ass` desde segmentos y estilo básico.
- `render_service.py`: quemado de subtítulos con FFmpeg usando filtro ASS.
- Endpoints añadidos: `GET /jobs/{id}/transcript`, `PUT /jobs/{id}/transcript`, `POST /jobs/{id}/render` y `GET /jobs/{id}/download`.
- Edición de texto y tiempos validada con esquemas Pydantic.
- Renderizado en segundo plano con transición `transcribed → rendering → done`.
- Descarga del vídeo subtitulado mediante `FileResponse`.
- Errores de render capturados por job con estado `error` y mensaje legible.
- Render real validado con FFmpeg sobre un vídeo sintético de prueba.

---

## Fase 5 — Validación y manejo de errores

**Fecha**: 26/06/2026
**Resultado**: 7/7 tests aprobados

| Test | Resultado |
|------|-----------|
| `test_formato_no_soportado_retorna_400` | APROBADO |
| `test_archivo_demasiado_grande_retorna_413` | APROBADO |
| `test_video_ilegible_retorna_400` | APROBADO |
| `test_duracion_excedida_retorna_400` | APROBADO |
| `test_logger_configurado_con_handler` | APROBADO |
| `test_mark_error_loguea` | APROBADO |
| `test_excepcion_inesperada_retorna_500_limpio` | APROBADO |

### Resumen Fase 5
- Validación de entrada confirmada: formato no soportado (400), tamaño excedido (413),
  vídeo ilegible (400) y duración excedida (400) con mensajes claros.
- Nuevo módulo `app/logger.py`: logging estructurado a stdout (formato con fecha, nivel y
  origen), nivel `INFO`, namespace `subtitulator.*`.
- Logging integrado en el pipeline: creación de job, extracción de audio, transcripción,
  render y errores; registro del `stderr` de FFmpeg en `audio_service` y `render_service`.
- Manejador global de excepciones en FastAPI: errores inesperados → HTTP 500 con JSON
  limpio (`{"detail": "Error interno del servidor"}`) sin exponer trazas internas.
- Verificado que la limpieza de temporales y el contrato de errores por job (estado
  `error` + mensaje legible) siguen intactos.

---

## Fase 6 — Frontend

**Fecha**: 26/06/2026
**Stack**: React 18 + Vite 5 + TypeScript + Tailwind 3 + Framer Motion
**Resultado tests**: 12/12 tests aprobados (Vitest) · build de producción correcto

| Test | Resultado |
|------|-----------|
| `time.test.ts › formatTimecode` (2) | APROBADO |
| `time.test.ts › parseTimecode` (3) | APROBADO |
| `client.test.ts › createJob` (2) | APROBADO |
| `client.test.ts › manejo de errores` (1) | APROBADO |
| `client.test.ts › downloadUrl` (1) | APROBADO |
| `UploadView.test.tsx` (3) | APROBADO |

### Resumen Fase 6
- Aplicación React + Vite + TS + Tailwind con estética «estudio de subtítulos»
  (tinta profunda, acento ámbar, tipografías Bricolage Grotesque / DM Sans / JetBrains Mono).
- Diseño guiado por las skills `/ui-ux-pro-max` y `/frontend-design`.
- Pantallas implementadas: subida (drag&drop + idioma + modelo), progreso con polling,
  editor de transcripción (texto y timecodes editables), panel de estilo básico con vista
  previa en vivo, descarga e historial deslizable.
- Cliente API tipado (`src/api/client.ts`) contra todos los endpoints del backend.
- Hook `useJobPolling` para sondeo de estado mientras el job está activo.
- Accesibilidad: labels en formularios, `aria-label` en botones de icono,
  `prefers-reduced-motion` respetado, foco visible.
- `Dockerfile` multietapa (build Vite + nginx) y servicio `frontend` añadido a
  `docker-compose.yml` (puerto 5173 → 80).
- Build de producción verificado: `tsc` + `vite build` sin errores
  (CSS 19 kB, JS 282 kB → 90 kB gzip).

### Observaciones Fase 6
- `npm audit` reporta vulnerabilidades en dependencias transitivas de desarrollo
  (cadena de build/test); no afectan al bundle de producción servido.

---

## Fase 7 — Integración y pulido

**Fecha**: 26/06/2026
**Resultado**: 3/3 tests aprobados · `docker compose config` válido

| Test | Resultado |
|------|-----------|
| `test_pipeline_e2e_completo` | APROBADO |
| `test_validacion_y_transcripcion_no_interfieren_entre_jobs` | APROBADO |
| `test_render_antes_de_transcribir_devuelve_409` | APROBADO |

### Resumen Fase 7
- Test end-to-end del flujo completo vía HTTP: subir → transcribir (background) →
  obtener transcripción → editar y guardar → renderizar (background) → descargar,
  validando estados `pending → processing → transcribed → rendering → done`.
- Verificado el aislamiento entre jobs: un job inválido (formato no soportado) no
  afecta a otro válido en curso.
- Generación real del archivo `.ass` durante el render e2e (Whisper y FFmpeg simulados).
- `docker-compose.yml` validado con `docker compose config` (servicios `backend` y
  `frontend` + volúmenes de modelos y datos).

---

## Ejecución completa (Backend)

**Fecha**: 26/06/2026
**Comando**: `pytest`
**Resultado global**: 57/57 tests aprobados

| Suite | Resultado |
|-------|-----------|
| `tests/test_fase1.py` | 19/19 APROBADOS |
| `tests/test_fase2.py` | 11/11 APROBADOS |
| `tests/test_fase3.py` | 8/8 APROBADOS |
| `tests/test_fase4.py` | 9/9 APROBADOS |
| `tests/test_fase5.py` | 7/7 APROBADOS |
| `tests/test_fase7.py` | 3/3 APROBADOS |

## Ejecución completa (Frontend)

**Fecha**: 26/06/2026
**Comando**: `npm run test` · `npm run build`
**Resultado global**: 12/12 tests aprobados · build de producción correcto

| Suite | Resultado |
|-------|-----------|
| `src/test/time.test.ts` | 5/5 APROBADOS |
| `src/test/client.test.ts` | 4/4 APROBADOS |
| `src/test/UploadView.test.tsx` | 3/3 APROBADOS |

### Observaciones
- Se mantiene una advertencia externa de `fastapi.testclient` sobre compatibilidad futura con `httpx`.
- No se ejecutó Whisper real en los tests de fases 3, 4, 5 y 7; se usaron mocks para validar
  el contrato de jobs y el pipeline sin coste ni dependencia del modelo descargado.
- El flujo e2e con Whisper y FFmpeg reales se ejecuta levantando `docker compose up`.
