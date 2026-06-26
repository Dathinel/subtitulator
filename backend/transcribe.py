import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.audio_service import extraer_audio, obtener_duracion
from app.services.transcription_service import transcribir


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <video_path> [idioma]")
        sys.exit(1)

    video_path = sys.argv[1]
    idioma = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Video: {video_path}")
    print(f"Idioma: {idioma or 'auto'}")

    print("\n[1/3] Detectando duracion...")
    duracion = obtener_duracion(video_path)
    print(f"  Duracion: {duracion:.1f}s")

    print("\n[2/3] Extrayendo audio...")
    audio_path = extraer_audio(video_path)
    print(f"  Audio extraido: {audio_path}")
    audio_size = os.path.getsize(audio_path)
    print(f"  Tamano: {audio_size / 1024:.1f} KB")

    print("\n[3/3] Transcribiendo...")
    try:
        segmentos = transcribir(audio_path, idioma)
        print(f"  Segmentos obtenidos: {len(segmentos)}")

        for i, seg in enumerate(segmentos):
            print(f"  [{seg['inicio']:.1f}s - {seg['fin']:.1f}s] {seg['texto']}")

        output = {
            "video": video_path,
            "duracion": duracion,
            "segmentos": segmentos,
        }
        output_path = os.path.splitext(video_path)[0] + "_transcript.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\nTranscripcion guardada en: {output_path}")
    except Exception as e:
        print(f"  Error: {e}")
        sys.exit(2)
    finally:
        if os.path.isfile(audio_path):
            os.remove(audio_path)
            print("  Audio temporal eliminado")


if __name__ == "__main__":
    main()
