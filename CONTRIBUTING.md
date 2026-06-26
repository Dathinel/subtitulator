# Guía de contribución

¡Gracias por tu interés en mejorar **Subtitulator**! Esta guía resume cómo poner el
proyecto en marcha y el proceso para contribuir.

## Poner en marcha el entorno

Sigue la sección **Instalación → Opción B (Local)** del [README](README.md) para levantar
backend y frontend en desarrollo. Necesitas **Python 3.11**, **Node 20** y **FFmpeg**
instalado en el sistema.

## Antes de abrir un Pull Request

1. **Crea una rama** descriptiva desde `main` (`feat/…`, `fix/…`, `docs/…`).
2. **Asegúrate de que los tests pasan:**
   ```bash
   cd backend && pytest
   cd frontend && npm test && npm run build
   ```
3. **Añade tests** para el comportamiento nuevo o corregido.
4. **Actualiza la documentación** afectada (`README.md`, `docs/`).
5. Mantén el **estilo del código** existente y los mensajes en español.

## Convención de commits

Usamos prefijos tipo *Conventional Commits*:

- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `docs:` documentación
- `test:` tests
- `refactor:` refactor sin cambio de comportamiento
- `chore:` mantenimiento

## Reportar bugs o proponer features

Abre un *issue* usando las plantillas disponibles. Incluye pasos de reproducción,
comportamiento esperado y entorno (SO, versión de FFmpeg, navegador).

## Principios del proyecto

- Es una **automatización determinista** (Whisper + FFmpeg), no un agente.
- **YAGNI**: evita añadir complejidad fuera del alcance acordado en [`docs/plan/plan.md`](docs/plan/plan.md).
- La transcripción es **local**; no introduzcas dependencias de APIs de pago.
