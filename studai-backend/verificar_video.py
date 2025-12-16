#!/usr/bin/env python3
"""
Script para verificar que el video base existe y tiene las características correctas.
"""
import os
from pathlib import Path

# Ruta del video base
BASE_VIDEO = "assets/content/MC/mc1.mp4"

def verificar_video():
    """Verifica que el video base existe y muestra información sobre él."""
    
    # Verificar si existe
    if not os.path.exists(BASE_VIDEO):
        print(f"❌ ERROR: El video base NO existe en: {BASE_VIDEO}")
        print(f"\n📁 Ruta absoluta esperada: {os.path.abspath(BASE_VIDEO)}")
        print(f"\n💡 Solución:")
        print(f"   1. Coloca un archivo llamado 'mc1.mp4' en la carpeta:")
        print(f"      {os.path.abspath('assets/content/MC')}")
        print(f"   2. O cambia la ruta en main.py línea 143")
        return False
    
    # Verificar que es un archivo
    if not os.path.isfile(BASE_VIDEO):
        print(f"❌ ERROR: {BASE_VIDEO} existe pero no es un archivo")
        return False
    
    # Obtener información del archivo
    file_size = os.path.getsize(BASE_VIDEO)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Video base encontrado: {BASE_VIDEO}")
    print(f"   📁 Ruta absoluta: {os.path.abspath(BASE_VIDEO)}")
    print(f"   📦 Tamaño: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    
    # Intentar obtener más información si moviepy está disponible
    try:
        from moviepy import VideoFileClip
        clip = VideoFileClip(BASE_VIDEO)
        print(f"   ⏱️  Duración: {clip.duration:.2f} segundos")
        print(f"   📐 Resolución: {clip.size[0]}x{clip.size[1]}")
        print(f"   🎬 FPS: {clip.fps}")
        clip.close()
        
        # Verificar que tiene suficiente duración (mínimo 10 segundos recomendado)
        if clip.duration < 10:
            print(f"\n⚠️  ADVERTENCIA: El video es muy corto ({clip.duration:.2f}s)")
            print(f"   Se recomienda al menos 30-60 segundos para tener suficiente contenido")
        
    except ImportError:
        print(f"   ℹ️  Instala moviepy para ver más detalles: pip install moviepy")
    except Exception as e:
        print(f"   ⚠️  No se pudo leer información del video: {e}")
    
    return True

if __name__ == "__main__":
    print("🔍 Verificando video base...\n")
    if verificar_video():
        print("\n✅ Todo listo! Puedes generar videos.")
    else:
        print("\n❌ Corrige el problema antes de generar videos.")
        exit(1)

