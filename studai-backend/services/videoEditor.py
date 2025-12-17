# ============================================================================
# SERVICIO DE EDICION DE VIDEO Y TRANSCRIPCION DE AUDIO
# ============================================================================
# Este archivo implementa:
# 1. Edicion de video (MoviePy - NO es IA, es procesamiento de video)
# 2. TRANSCRIPCION DE AUDIO (Speech-to-Text) usando AssemblyAI (IA)
# RELACION CON IA:
# - IA_Clase_02 (Topicos de IA): Transcripcion de audio es procesamiento de lenguaje
# - IA_Clase_05 (Modelos de Lenguaje): Los modelos convierten audio a texto
# TECNOLOGIA: AssemblyAI para transcripcion de audio
# ============================================================================

# ============================================================================
# IMPORTACIONES
# ============================================================================
import os  # Para operaciones del sistema de archivos y variables de entorno
import random  # Para seleccionar segmentos aleatorios del video
import subprocess  # Para ejecutar comandos externos (ffmpeg)
import shutil  # Para buscar ejecutables en el PATH del sistema
from typing import Tuple  # Para tipado: indica que una funcion retorna una tupla

# MoviePy: Biblioteca para edicion de video (NO es IA, es procesamiento de video)
from moviepy import VideoFileClip, AudioFileClip

# AssemblyAI: Servicio de IA para transcripcion de audio (Speech-to-Text)
# Relacion: IA_Clase_02 (Topicos de IA), IA_Clase_05 (Modelos de Lenguaje)
import assemblyai as aai

# ============================================================================
# CONFIGURACION DE ASSEMBLYAI (SERVICIO DE IA PARA TRANSCRIPCION)
# ============================================================================
# AssemblyAI usa modelos de IA para convertir audio hablado en texto
# Esta configuracion se usa solo si se llama la funcion transcribe_audio()
# (que actualmente NO se usa en el flujo principal)
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# ============================================================================
# CONFIGURACION DE FUENTES Y DIRECTORIOS
# ============================================================================
FONTS_DIR = "assets/fonts"  # Directorio donde estan las fuentes para subtitulos
DEFAULT_FONT_NAME = "Gilroy-Bold"  # Fuente por defecto para subtitulos


def videoEditor(video_path: str, audio_path: str, language: str, output_path: str | None = None) -> str:
    """
    Editor de video simplificado que combina video base con audio generado.
    
    NOTA: Esta funcion NO usa IA, solo procesamiento de video normal.
    La edicion de video (cortar, recortar, sincronizar) es procesamiento de video tradicional.
    
    Proceso:
      1) Corta un segmento aleatorio del video base segun la duracion del audio (MoviePy)
      2) Recorta a formato vertical 9:16 (para redes sociales como TikTok, Instagram)
      3) Sincroniza el audio generado con el video
      4) Exporta un MP4 temporal (sin quemar subtitulos)
    
    Parametros:
        video_path (str): Ruta al video base que se editara
        audio_path (str): Ruta al archivo de audio generado por TTS
        language (str): Idioma del audio ('spanish' o 'english') - no se usa actualmente
        output_path (str | None): Ruta donde guardar el video final (opcional)
    
    Retorna:
        str: Ruta del MP4 generado (sin subtitulos)
    
    Lanza:
        FileNotFoundError: Si el archivo de audio no existe
    """
    # ========================================================================
    # VALIDACION DE ARCHIVOS
    # ========================================================================
    # Verificar que el archivo de audio existe antes de continuar
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # ========================================================================
    # CREACION DE DIRECTORIOS
    # ========================================================================
    # Crear los directorios necesarios si no existen
    os.makedirs("output/temp", exist_ok=True)    # Para archivos temporales
    os.makedirs("output/videos", exist_ok=True)  # Para videos finales

    # ========================================================================
    # DETERMINACION DE NOMBRES DE ARCHIVOS
    # ========================================================================
    # Extraer el nombre base del archivo de salida (sin extension)
    final_basename = None
    if output_path:
        # Si se proporciono una ruta de salida, extraer el nombre base
        final_basename = os.path.splitext(os.path.basename(output_path))[0]
    else:
        # Si no se proporciono, usar un nombre por defecto
        final_basename = "final_output"
        output_path = os.path.join("output/videos", f"{final_basename}.mp4")

    # Ruta para el video temporal (antes de procesar)
    temp_video_path = os.path.join("output/temp", f"{final_basename}_temp.mp4")

    # ========================================================================
    # EDICION DEL VIDEO
    # ========================================================================
    # Esta funcion hace todo el trabajo de edicion:
    # - Corta un segmento aleatorio del video
    # - Recorta a formato vertical
    # - Sincroniza el audio
    # - Exporta el video final
    print(f"🎬 Generando video sin subtítulos...")
    base_edit_export(video_path, audio_path, temp_video_path)
    print(f"✅ Video generado: {temp_video_path}")

    # ========================================================================
    # GENERAR Y QUEMAR SUBTITULOS
    # ========================================================================
    print(f"\n{'='*60}")
    print(f"📝 INICIANDO GENERACION DE SUBTITULOS")
    print(f"{'='*60}")
    
    # Verificar que AssemblyAI API key esté configurada
    assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not assemblyai_key:
        print(f"⚠️  ASSEMBLYAI_API_KEY no configurada en variables de entorno")
        print(f"   Saltando generacion de subtitulos...")
        print(f"   Para activar subtitulos, configura ASSEMBLYAI_API_KEY")
        return temp_video_path
    
    print(f"✅ ASSEMBLYAI_API_KEY encontrada: {assemblyai_key[:10]}...")
    
    try:
        
        # Transcribir audio usando IA (AssemblyAI)
        print(f"   🎤 Transcribiendo audio con AssemblyAI...")
        text, words = transcribe_audio(audio_path, language)
        
        if not words or len(words) == 0:
            print(f"⚠️  No se obtuvieron palabras de la transcripción. Saltando subtítulos...")
            return temp_video_path
        
        print(f"   ✅ Obtuvidas {len(words)} palabras para subtítulos")
        
        # Crear archivo SRT
        print(f"   📄 Creando archivo SRT...")
        srt_path = os.path.join("output/temp", f"{final_basename}.srt")
        create_srt(words, srt_path, max_words_per_subtitle=10)
        
        # Verificar que el archivo SRT se creó
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"SRT file not created: {srt_path}")
        print(f"   ✅ Archivo SRT creado: {srt_path}")
        
        # Convertir SRT a ASS (formato para quemar subtítulos)
        print(f"   🔄 Convirtiendo SRT a ASS...")
        ass_path = os.path.join("output/temp", f"{final_basename}.ass")
        # Usar fuente más grande (56px) para mejor legibilidad en videos verticales
        convert_srt_to_ass(srt_path, ass_path, font_name=DEFAULT_FONT_NAME, font_size=56)
        
        # Verificar que el archivo ASS se creó
        if not os.path.exists(ass_path):
            raise FileNotFoundError(f"ASS file not created: {ass_path}")
        print(f"   ✅ Archivo ASS creado: {ass_path}")
        
        # Verificar que el directorio de fuentes existe
        if not os.path.exists(FONTS_DIR):
            print(f"⚠️  Directorio de fuentes no encontrado: {FONTS_DIR}")
            print(f"   Creando directorio...")
            os.makedirs(FONTS_DIR, exist_ok=True)
        
        # Quemar subtítulos en el video usando FFmpeg
        print(f"🔥 Quemando subtítulos en el video con FFmpeg...")
        final_video_with_subs = output_path if output_path else os.path.join("output/videos", f"{final_basename}_final.mp4")
        burn_subtitles_ffmpeg(temp_video_path, ass_path, final_video_with_subs, FONTS_DIR)
        print(f"✅ Video con subtítulos generado: {final_video_with_subs}")
        
        return final_video_with_subs
    except Exception as subtitle_error:
        print(f"⚠️  Error al generar subtítulos: {subtitle_error}")
        print(f"   Continuando sin subtítulos...")
        import traceback
        traceback.print_exc()
        # Si falla, retornar video sin subtítulos
        return temp_video_path


# ============================================================================
# FUNCIONES AUXILIARES (NO SON IA - SOLO PROCESAMIENTO DE VIDEO)
# ============================================================================

def base_edit_export(video_path: str, audio_path: str, temp_output: str) -> None:
    """
    Exporta un video MP4 temporal con recorte vertical y audio sincronizado.
    
    NOTA: Esta funcion NO usa IA, solo procesamiento de video normal.
    
    Proceso:
      1. Carga el audio y obtiene su duracion
      2. Extrae un segmento aleatorio del video de esa duracion
      3. Recorta el video a formato vertical 9:16
      4. Sincroniza el audio con el video
      5. Exporta el video final como MP4
    
    Parametros:
        video_path (str): Ruta al video base
        audio_path (str): Ruta al archivo de audio
        temp_output (str): Ruta donde guardar el video editado
    """
    # Cargar el archivo de audio usando MoviePy
    audio = AudioFileClip(audio_path)
    # Obtener la duracion del audio en segundos
    audio_length = audio.duration

    # Extraer un segmento aleatorio del video que tenga la misma duracion que el audio
    video_clip = extract_random_video_clip(video_path, audio_length)
    
    # Recortar el video a formato vertical (9:16) para redes sociales
    video_clip = crop_to_vertical(video_clip)
    
    # Reemplazar el audio del video con el audio generado por TTS
    final_clip = video_clip.with_audio(audio)

    # Exportar el video final como MP4
    final_clip.write_videofile(
        temp_output,              # Ruta de salida
        codec="libx264",          # Codificador de video (H.264)
        audio_codec="aac",       # Codificador de audio (AAC)
        fps=30,                   # Frames por segundo
        preset="ultrafast",       # Preset de codificacion (rapido pero menos comprimido)
        threads=4,                # Numero de hilos para procesamiento paralelo
        temp_audiofile="output/temp/temp-audio.m4a",  # Archivo temporal de audio
        remove_temp=True          # Eliminar archivos temporales al finalizar
    )


def extract_random_video_clip(video_path: str, duration: float) -> VideoFileClip:
    """
    Extrae un segmento aleatorio del video de una duracion especifica.
    
    NOTA: Esta funcion NO usa IA, solo procesamiento de video normal.
    
    Parametros:
        video_path (str): Ruta al video base
        duration (float): Duracion del segmento a extraer en segundos
    
    Retorna:
        VideoFileClip: Segmento del video de la duracion especificada
    
    Lanza:
        ValueError: Si el video es mas corto que la duracion requerida
    """
    # Cargar el video completo
    video = VideoFileClip(video_path)
    
    # Calcular el tiempo maximo de inicio posible
    # Si el video dura 60s y necesitamos 30s, podemos empezar hasta el segundo 30
    max_start_time = video.duration - duration
    
    # Verificar que el video sea suficientemente largo
    if max_start_time <= 0:
        raise ValueError("The video is shorter than the audio duration.")
    
    # Seleccionar un tiempo de inicio aleatorio entre 0 y max_start_time
    start_time = random.uniform(0, max_start_time)
    
    # Extraer el segmento desde start_time hasta start_time + duration
    return video.subclipped(start_time, start_time + duration)


def crop_to_vertical(video_clip: VideoFileClip) -> VideoFileClip:
    """
    Recorta el video a formato vertical 9:16 (para redes sociales).
    
    NOTA: Esta funcion NO usa IA, solo procesamiento de video normal.
    
    El formato 9:16 es el formato vertical usado en TikTok, Instagram Reels, etc.
    Si el video es horizontal, se recorta desde el centro.
    
    Parametros:
        video_clip (VideoFileClip): Video a recortar
    
    Retorna:
        VideoFileClip: Video recortado a formato vertical
    
    Lanza:
        ValueError: Si el video es demasiado estrecho para recortar a vertical
    """
    # Ratio de aspecto objetivo: 9:16 (vertical)
    target_aspect_ratio = 9 / 16
    
    # Obtener las dimensiones originales del video
    original_width, original_height = video_clip.size
    
    # Calcular el ancho nuevo basado en la altura y el ratio objetivo
    # Si la altura es 1920px, el ancho debe ser 1080px (9:16)
    new_width = int(original_height * target_aspect_ratio)

    # Verificar que el video original sea mas ancho que el nuevo ancho
    if original_width > new_width:
        # Calcular el centro horizontal del video
        x_center = original_width // 2
        
        # Calcular los limites izquierdo y derecho del recorte
        # Se recorta desde el centro hacia los lados
        x1 = x_center - new_width // 2  # Limite izquierdo
        x2 = x_center + new_width // 2   # Limite derecho
        
        # Recortar el video horizontalmente (mantener toda la altura)
        return video_clip.cropped(x1=x1, x2=x2)
    else:
        # Si el video ya es muy estrecho, no se puede recortar
        raise ValueError("The video is too narrow to be cropped to vertical format.")


def transcribe_audio(audio_path: str, language: str) -> Tuple[str, list]:
    """
    Transcribe audio a texto usando SPEECH-TO-TEXT (STT) con IA.
    
    RELACION CON IA:
    - IA_Clase_02 (Topicos de IA): Transcripcion de audio es procesamiento de lenguaje
    - IA_Clase_05 (Modelos de Lenguaje): Usa modelos neurales para reconocer palabras en audio
    
    TECNOLOGIA: AssemblyAI
    - Convierte audio hablado en texto transcrito
    - Obtiene timestamps a nivel de palabra para sincronizacion
    - Soporta ingles y espanol automaticamente
    
    NOTA: Esta funcion esta implementada pero NO se usa actualmente en el flujo principal.
    Si se quisiera agregar subtitulos, se llamaria esta funcion.
    """
    # Verificar que la clave de API este configurada
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError("ASSEMBLYAI_API_KEY environment variable is not set")
    
    print(f"   📡 Using AssemblyAI API key: {api_key[:10]}...")
    print(f"   🌐 Language: {language} -> {map_language(language)}")
    print(f"   📁 Audio file: {audio_path}")
    
    # Mapear idioma al codigo que AssemblyAI requiere
    language_code = map_language(language)
    # Inicializar el transcriber (componente de IA)
    transcriber = aai.Transcriber()
    
    print(f"   ⏳ Starting transcription...")
    # LLAMADA A LA IA: Enviar audio para transcripcion
    # El modelo neural de AssemblyAI procesa el audio y genera texto
    transcript = transcriber.transcribe(
        audio_path,
        config=aai.TranscriptionConfig(
            language_code=language_code,
            punctuate=True,      # Agregar puntuacion (IA)
            format_text=True,    # Formatear texto (IA)
            speaker_labels=False,
            auto_chapters=False
        )
    )
    
    print(f"   ⏳ Waiting for transcription to complete...")
    # Esperar a que el modelo de IA termine de procesar
    while transcript.status not in ["completed", "error"]:
        import time
        time.sleep(1)
        transcript = transcriber.get_transcript(transcript.id)
        if transcript.status == "processing":
            print(f"   ⏳ Still processing...")
    
    if transcript.status == "error":
        error_msg = getattr(transcript, 'error', 'Unknown error')
        raise Exception(f"Transcription failed: {error_msg}")

    # Extraer el texto transcrito y los timestamps de palabras
    # Los timestamps permiten sincronizar subtitulos con el audio
    # AssemblyAI devuelve timestamps en milisegundos
    text = transcript.text or ""
    words = []
    for w in (transcript.words or []):
        # AssemblyAI devuelve timestamps en milisegundos
        words.append({
            "start": int(w.start),  # Ya está en milisegundos
            "end": int(w.end),      # Ya está en milisegundos
            "text": w.text
        })
    print(f"   ✅ Transcription completed: {len(text)} characters, {len(words)} words")
    return text, words


def map_language(language: str) -> str:
    if language == "spanish":
        return "es"
    elif language == "english":
        return "en"
    else:
        return "en"


def create_srt(words: list, srt_file_path: str, max_words_per_subtitle: int = 8) -> None:
    """
    Create SRT file from word-level information.
    Agrupa palabras en frases para subtítulos más legibles.
    
    Parametros:
        words (list): Lista de palabras con timestamps
        srt_file_path (str): Ruta donde guardar el archivo SRT
        max_words_per_subtitle (int): Máximo de palabras por subtítulo (default: 8)
    """
    os.makedirs(os.path.dirname(srt_file_path), exist_ok=True)
    
    if not words:
        print("   ⚠️  No words provided for subtitles")
        return
    
    # AssemblyAI devuelve timestamps en milisegundos
    subtitle_index = 1
    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        i = 0
        while i < len(words):
            # Agrupar palabras en frases (máximo max_words_per_subtitle palabras)
            subtitle_words = []
            start_time_ms = words[i]["start"]  # Ya está en milisegundos
            end_time_ms = words[i]["end"]
            
            # Agrupar palabras hasta max_words_per_subtitle o hasta encontrar puntuación
            j = i
            while j < len(words) and len(subtitle_words) < max_words_per_subtitle:
                word = words[j]
                subtitle_words.append(word["text"])
                end_time_ms = word["end"]  # Actualizar tiempo final
                
                # Si la palabra termina con puntuación fuerte, terminar la frase aquí
                if word["text"].strip().endswith(('.', '!', '?')):
                    j += 1
                    break
                
                j += 1
            
            # Formatear tiempos (format_time espera milisegundos)
            start = format_time(int(start_time_ms))
            end = format_time(int(end_time_ms))
            
            # Crear texto del subtítulo (mantener formato original)
            subtitle_text = " ".join(subtitle_words)
            
            # Escribir entrada SRT
            srt_file.write(f"{subtitle_index}\n{start} --> {end}\n{subtitle_text}\n\n")
            subtitle_index += 1
            
            i = j
    
    print(f"   ✅ SRT file written: {srt_file_path} ({subtitle_index - 1} subtitle entries from {len(words)} words)")


def format_time(ms: int) -> str:
    total_seconds = ms / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def convert_srt_to_ass(srt_path: str, ass_path: str, font_name: str = "Gilroy-Bold", font_size: int = 56) -> None:
    """
    Convert SRT to ASS format with centered styling.
    
    Parametros:
        srt_path (str): Ruta al archivo SRT
        ass_path (str): Ruta donde guardar el archivo ASS
        font_name (str): Nombre de la fuente (default: "Gilroy-Bold")
        font_size (int): Tamaño de fuente en píxeles (default: 56 para mejor legibilidad en videos verticales)
    """
    # ASS header with centered alignment
    # Outline más grueso (4 en lugar de 3) y shadow más visible (2) para mejor legibilidad
    # MarginV más grande (50 en lugar de 10) para posicionar subtítulos más abajo
    ass_header = f"""[Script Info]
Title: Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,5,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    with open(ass_path, 'w', encoding='utf-8') as ass_file:
        ass_file.write(ass_header)
        
        # Read SRT and convert to ASS format
        # Try different encodings to handle various file formats
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(srt_path, 'r', encoding=encoding) as srt_file:
                    content = srt_file.read()
                print(f"   ✅ SRT file read successfully with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"   ⚠️ Error reading with {encoding}: {e}")
                continue
        
        if content is None:
            raise Exception(f"Could not read SRT file {srt_path} with any encoding")
            
        # Parse SRT entries
        entries = content.strip().split('\n\n')
        print(f"   📝 Found {len(entries)} subtitle entries")
        
        for entry in entries:
            lines = entry.split('\n')
            if len(lines) >= 3:
                # Parse timing (line 1 is index, line 2 is timing)
                timing = lines[1].replace(',', '.')
                if ' --> ' not in timing:
                    continue
                start, end = timing.split(' --> ')
                start = start.strip()[:11]  # Remove milliseconds beyond .xx
                end = end.strip()[:11]
                
                # Get text (lines 2+ are the subtitle text)
                text = ' '.join(lines[2:]).strip()
                
                # Skip empty entries
                if not text:
                    continue
                
                # Write ASS dialogue line
                ass_file.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
        
        print(f"   ✅ ASS file created successfully: {ass_path}")


def burn_subtitles_ffmpeg(
    input_video: str,
    ass_path: str,
    output_video: str,
    fonts_dir: str
) -> None:

    os.makedirs(os.path.dirname(output_video), exist_ok=True)

    # Use absolute POSIX-like paths for ffmpeg
    from pathlib import Path
    ass_abs = Path(ass_path).resolve().as_posix()
    fonts_abs = Path(fonts_dir).resolve().as_posix()
    input_abs = Path(input_video).resolve().as_posix()
    output_abs = Path(output_video).resolve().as_posix()

    # Escape colons for Windows and quote values to avoid parse errors
    ass_q = ass_abs.replace(":", r"\:")
    fonts_q = fonts_abs.replace(":", r"\:")
    vf_expr = f"ass=filename='{ass_q}':fontsdir='{fonts_q}'"
    print(f"🔧 FFmpeg filter: {vf_expr}")

    # Find ffmpeg in PATH or use environment variable
    ffmpeg_bin = os.getenv("FFMPEG_PATH")
    
    # If FFMPEG_PATH is set, verify it exists
    if ffmpeg_bin:
        if not os.path.exists(ffmpeg_bin):
            print(f"⚠️ FFMPEG_PATH set to {ffmpeg_bin} but file doesn't exist. Searching in PATH...")
            ffmpeg_bin = None
    
    # If not set or invalid, search in PATH
    if not ffmpeg_bin:
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            raise RuntimeError("ffmpeg not found in PATH. Please install ffmpeg or set FFMPEG_PATH environment variable.")
    
    # Verify the file exists
    if not os.path.exists(ffmpeg_bin):
        raise FileNotFoundError(f"ffmpeg executable not found at: {ffmpeg_bin}")
    
    print(f"✅ Using ffmpeg: {ffmpeg_bin}")

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", input_abs,
        "-vf", vf_expr,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "copy",
        output_abs
    ]

    print(f"   🔧 Ejecutando FFmpeg: {' '.join(cmd[:3])} ... [video filter] ... {output_abs}")
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minutos timeout
        )
        if result.stdout:
            print(f"   📝 FFmpeg stdout: {result.stdout[:200]}...")
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg timeout after 5 minutes")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ FFmpeg error (exit code {e.returncode}):")
        if e.stdout:
            print(f"   stdout: {e.stdout[:500]}")
        if e.stderr:
            print(f"   stderr: {e.stderr[:500]}")
        raise

if __name__ == "__main__":
    # Simple manual test (requires ASSEMBLYAI_API_KEY and files to exist)
    base_video = "assets/content/MC/mc1.mp4"
    audio_file = "output/audio/output.mp3"
    out_path = "output/videos/manual_test_final_video_spanish.mp4"
    print(videoEditor(base_video, audio_file, "spanish", out_path))