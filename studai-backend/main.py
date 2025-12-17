# ============================================================================
# AGENTE INTELIGENTE - ORQUESTADOR DEL PIPELINE DE IA
# ============================================================================
# Este archivo actua como un AGENTE INTELIGENTE que orquesta todo el proceso.
# RELACION CON IA:
# - IA_Clase_03 (Agentes Inteligentes): Este es un agente que percibe, decide y actua
# - IA_Clase_04 (Tipos de Agentes): Es un agente reactivo que responde a peticiones HTTP
# 
# El agente integra multiples tecnologias de IA:
# 1. NLP + OCR: Extraccion de texto de PDFs (genScript.py)
# 2. LLM: Generacion de guiones (genScript.py - Azure OpenAI GPT)
# 3. TTS: Generacion de audio (genTTS.py - Azure Cognitive Services)
# 4. STT: Transcripcion de audio (videoEditor.py - AssemblyAI, opcional)
# ============================================================================

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, BackgroundTasks
import os, uuid, shutil, asyncio
import requests
import re
from typing import Dict, Optional
from datetime import datetime
# Importar servicios de IA
from services.genScript import extract_text_from_pdf, generate_short_video_script, client, deployment
from services import genTTS, videoEditor
from utils.azure_blob import upload_to_blob
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pathlib import Path
app = FastAPI()

# ============================================================================
# SISTEMA DE JOBS PARA PROCESAMIENTO ASINCRONO
# ============================================================================
# Almacena el estado de los jobs de generacion de video
# En produccion, considera usar Redis o una base de datos
jobs: Dict[str, Dict] = {}

# Configurar CORS: permite requests desde frontend local y produccion
# En produccion, agrega tu dominio de Render o Vercel aqui
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Agrega tu dominio de produccion aqui cuando despliegues:
    # "https://tu-frontend.onrender.com",
    # "https://tu-frontend.vercel.app",
]

# Permitir todos los origenes en desarrollo (solo para testing)
# En produccion, especifica solo los dominios permitidos
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,  # set True only if you use cookies/auth
)

BASE_DIR = Path("/Users/martinortiz/Desktop/Cloud_School/studai-backend/output/videos").resolve()

# ============================================================================
# FUNCION PARA OBTENER VIDEO BASE (DESCARGAR DESDE URL SI ES NECESARIO)
# ============================================================================
def convert_google_drive_link(url: str) -> str:
    """
    Convierte un link de Google Drive a formato de descarga directa.
    
    Parametros:
        url (str): Link de Google Drive (ej: https://drive.google.com/file/d/FILE_ID/view)
    
    Retorna:
        str: Link de descarga directa
    """
    # Extraer el FILE_ID del link de Google Drive
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        # Para archivos grandes, usar confirm=t para evitar página de advertencia
        return f"https://drive.google.com/uc?export=download&confirm=t&id={file_id}"
    
    # Si ya es un link uc?, extraer el ID y reconstruirlo con confirm=t
    match_uc = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
    if match_uc:
        file_id = match_uc.group(1)
        return f"https://drive.google.com/uc?export=download&confirm=t&id={file_id}"
    
    return url

async def get_base_video() -> str:
    """
    Obtiene la ruta del video base. Si no existe localmente, lo descarga desde una URL.
    Soporta links de Google Drive y Azure Blob Storage.
    
    Retorna:
        str: Ruta local del video base
    
    Lanza:
        FileNotFoundError: Si el video no se encuentra y no se puede descargar
    """
    local_video_path = "assets/content/MC/mc1.mp4"
    
    # Si el video existe localmente, usarlo
    if os.path.exists(local_video_path):
        print(f"✅ Video base encontrado localmente: {local_video_path}")
        return local_video_path
    
    # Si no existe, intentar descargarlo desde una URL
    video_url = os.getenv("BASE_VIDEO_URL")
    print(f"📥 Video base no encontrado localmente en: {local_video_path}")
    print(f"   BASE_VIDEO_URL configurada: {'Sí' if video_url else 'No'}")
    
    if not video_url:
        error_msg = (
            f"Video base no encontrado en '{local_video_path}' y BASE_VIDEO_URL no está configurada. "
            f"Configura la variable de entorno BASE_VIDEO_URL en Render con la URL del video "
            f"(Google Drive o Azure Blob Storage)."
        )
        print(f"❌ {error_msg}")
        raise FileNotFoundError(error_msg)
    
    print(f"📥 Descargando video base desde URL...")
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(local_video_path), exist_ok=True)
        print(f"   Directorio creado: {os.path.dirname(local_video_path)}")
        
        # Si es un link de Google Drive, convertirlo a descarga directa
        if "drive.google.com" in video_url:
            original_url = video_url
            video_url = convert_google_drive_link(video_url)
            print(f"   ✅ Link de Google Drive convertido:")
            print(f"      Original: {original_url[:80]}...")
            print(f"      Descarga: {video_url[:80]}...")
        
        # Descargar el video con mejor manejo de errores
        print(f"   Descargando desde: {video_url[:100]}...")
        
        # Intentar descargar con headers para evitar problemas con Google Drive
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Para Google Drive, usar sesión para manejar cookies y redirecciones
        session = requests.Session()
        response = session.get(video_url, stream=True, timeout=600, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        # Verificar si es HTML (página de error de Google Drive)
        content_type = response.headers.get('content-type', '').lower()
        print(f"   📄 Content-Type inicial: {content_type}")
        
        if 'text/html' in content_type:
            # Es una página HTML, probablemente Google Drive está bloqueando la descarga
            print(f"   ⚠️  Google Drive devolvió HTML. Esto significa que el archivo es demasiado grande o requiere permisos especiales.")
            print(f"   💡 SOLUCION: Sube el video a Azure Blob Storage y usa esa URL en BASE_VIDEO_URL")
            raise IOError(
                "Google Drive está bloqueando la descarga del archivo. "
                "El archivo puede ser demasiado grande (>100MB) o requiere permisos especiales. "
                "SOLUCION: Sube el video a Azure Blob Storage y usa esa URL en BASE_VIDEO_URL. "
                "Ejemplo: BASE_VIDEO_URL=https://studai.blob.core.windows.net/videos/mc1.mp4?[SAS_TOKEN]"
            )
        
        total_size = int(response.headers.get('content-length', 0))
        print(f"   ✅ Conexión establecida. Tamaño esperado: {total_size / (1024*1024):.2f} MB" if total_size > 0 else "   ✅ Conexión establecida. Tamaño: desconocido")
        print(f"   📄 Content-Type: {content_type}")
        
        # Guardar el video con verificación
        downloaded = 0
        temp_path = local_video_path + ".tmp"
        
        try:
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Mostrar cada MB
                                print(f"   Descargado: {percent:.1f}% ({downloaded // (1024*1024)} MB)")
            
            # Verificar que el archivo se descargó completamente
            if not os.path.exists(temp_path):
                raise FileNotFoundError(f"El archivo temporal no se creó: {temp_path}")
            
            file_size = os.path.getsize(temp_path)
            print(f"   📊 Archivo descargado: {file_size / (1024*1024):.2f} MB")
            
            # Verificar que no es HTML (primeros bytes)
            with open(temp_path, "rb") as f:
                first_bytes = f.read(1024)
                if b'<html' in first_bytes.lower() or b'<!doctype' in first_bytes.lower() or b'<head' in first_bytes.lower():
                    error_msg = (
                        f"El archivo descargado es HTML (página de error de Google Drive), no un video. "
                        f"Tamaño: {file_size} bytes. "
                        f"Google Drive bloquea descargas directas de archivos grandes. "
                        f"SOLUCION: Sube el video a Azure Blob Storage y usa esa URL en BASE_VIDEO_URL."
                    )
                    raise IOError(error_msg)
            
            # Verificar que el tamaño coincide (si se conoce)
            if total_size > 0 and abs(file_size - total_size) > 1024:  # Permitir 1KB de diferencia
                raise IOError(f"El archivo descargado está incompleto. Esperado: {total_size} bytes, Obtenido: {file_size} bytes")
            
            # Verificar que es un archivo MP4 válido (al menos debe tener un tamaño mínimo razonable)
            if file_size < 1024 * 100:  # Menos de 100KB probablemente está corrupto
                raise IOError(f"El archivo descargado es demasiado pequeño ({file_size} bytes), probablemente está corrupto o es una página de error")
            
            # Mover el archivo temporal al destino final
            if os.path.exists(local_video_path):
                os.remove(local_video_path)
            os.rename(temp_path, local_video_path)
            
            print(f"✅ Video base descargado exitosamente: {local_video_path} ({file_size / (1024*1024):.2f} MB)")
            
            # Verificar que el archivo es accesible
            if not os.path.exists(local_video_path):
                raise FileNotFoundError(f"El archivo no existe después de mover: {local_video_path}")
            
            return local_video_path
            
        except Exception as e:
            # Limpiar archivo temporal si existe
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            raise
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de red al descargar video base: {str(e)}"
        print(f"❌ {error_msg}")
        raise FileNotFoundError(error_msg)
    except Exception as e:
        error_msg = f"Error al descargar video base: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        raise FileNotFoundError(error_msg)

def get_file_path_safe(filename: str) -> Path:
    safe_name = Path(filename).name
    p = (BASE_DIR / safe_name).resolve()
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    if BASE_DIR not in p.parents and p != BASE_DIR:
        raise HTTPException(status_code=400, detail="Invalid path")
    return p

@app.get("/api/local-video/{filename}")
async def local_video(filename: str, request: Request):
    file_path = get_file_path_safe(filename)
    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")
    content_type = "video/mp4"

    if range_header:
        try:
            unit, rng = range_header.split("=")
            if unit != "bytes":
                raise ValueError
            start_s, end_s = rng.split("-")
            start = int(start_s) if start_s else 0
            end = int(end_s) if end_s else file_size - 1
            if start < 0 or start > end:
                raise ValueError
            end = min(end, file_size - 1)
        except Exception:
            raise HTTPException(status_code=416, detail="Malformed Range header")

        def iter_range(s: int, e: int, chunk: int = 1024 * 1024):
            with open(file_path, "rb") as f:
                f.seek(s)
                remaining = e - s + 1
                while remaining > 0:
                    data = f.read(min(chunk, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": content_type,
            "Cache-Control": "no-store",
        }
        return StreamingResponse(iter_range(start, end), status_code=206, headers=headers)

    def iter_full(chunk: int = 1024 * 1024):
        with open(file_path, "rb") as f:
            while True:
                data = f.read(chunk)
                if not data:
                    break
                yield data

    headers = {
        "Content-Length": str(file_size),
        "Accept-Ranges": "bytes",
        "Content-Type": "video/mp4",
        "Cache-Control": "no-store",
    }
    return StreamingResponse(iter_full(), media_type=content_type, headers=headers)

async def process_video_generation(
    job_id: str,
    file_id: str,
    local_path: Optional[str],
    blob_url: Optional[str],
    user_additional_input: str,
    script: str,
    audio_path: str,
    audio_url: str,
    language: str
):
    """
    Funcion que ejecuta la generacion de video en background.
    Actualiza el estado del job mientras procesa.
    """
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["message"] = "🎬 Generando video..."
        
        # Obtener ruta del video base
        try:
            base_video = await get_base_video()
        except FileNotFoundError as e:
            error_msg = f"Error al obtener video base: {str(e)}"
            print(f"❌ {error_msg}")
            jobs[job_id]["status"] = "error"
            jobs[job_id]["message"] = f"❌ Error: {error_msg}"
            jobs[job_id]["error"] = error_msg
            # Retornar resultados parciales (sin video)
            jobs[job_id]["result"] = {
                "script": script,
                "audio_url": audio_url,
                "video_url": None
            }
            if local_path:
                jobs[job_id]["result"]["pdf_name"] = file_id
                jobs[job_id]["result"]["pdf_blob_url"] = blob_url
            else:
                jobs[job_id]["result"]["topic"] = user_additional_input
            jobs[job_id]["completed_at"] = datetime.now().isoformat()
            return
        
        final_video_path = f"output/videos/{file_id}_final_video_{language}.mp4"
        
        print(f"   📹 Base video: {base_video}")
        print(f"   🎵 Audio path: {audio_path}")
        print(f"   📁 Output path: {final_video_path}")

        def render_video():
            try:
                print(f"   🎬 Iniciando videoEditor.videoEditor()...")
                result = videoEditor.videoEditor(base_video, audio_path, language, output_path=final_video_path)
                print(f"   ✅ videoEditor completado")
                return result
            except Exception as e:
                print(f"❌ Error in videoEditor: {e}")
                import traceback
                traceback.print_exc()
                raise

        print(f"   ⏳ Rendering video (this may take a while)...")
        jobs[job_id]["message"] = "⏳ Renderizando video (esto puede tardar varios minutos)..."
        
        # Ejecutar renderizado de video en thread separado
        final_video_burned_path = await asyncio.to_thread(render_video)
        print(f"✅ Video rendered: {final_video_burned_path}")
        
        if not os.path.exists(final_video_burned_path):
            raise FileNotFoundError(f"Video generado no encontrado: {final_video_burned_path}")
        
        file_size = os.path.getsize(final_video_burned_path)
        print(f"   📊 Tamaño del video: {file_size / (1024*1024):.2f} MB")
        
        jobs[job_id]["message"] = "⬆️ Subiendo video a Azure Blob Storage..."
        print(f"⬆️ Uploading video to blob storage...")
        video_url = await upload_to_blob(final_video_burned_path, f"videos/{file_id}_final_video_{language}.mp4")
        print(f"✅ Video uploaded: {video_url}")
        
        # Actualizar job con resultados
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = "✅ Video generado exitosamente"
        jobs[job_id]["result"] = {
            "script": script,
            "audio_url": audio_url,
            "video_url": video_url
        }
        if local_path:
            jobs[job_id]["result"]["pdf_name"] = file_id
            jobs[job_id]["result"]["pdf_blob_url"] = blob_url
        else:
            jobs[job_id]["result"]["topic"] = user_additional_input
        
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as video_error:
        print(f"❌ Error durante generacion de video: {video_error}")
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = f"❌ Error: {str(video_error)}"
        jobs[job_id]["error"] = str(video_error)
        # Retornar solo script y audio si falla el video
        jobs[job_id]["result"] = {
            "script": script,
            "audio_url": audio_url,
            "video_url": None
        }
        if local_path:
            jobs[job_id]["result"]["pdf_name"] = file_id
            jobs[job_id]["result"]["pdf_blob_url"] = blob_url
        else:
            jobs[job_id]["result"]["topic"] = user_additional_input

@app.post("/generate/video")
async def generate_video(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(None), 
    user_additional_input: str = Form(...)
):
    """
    AGENTE INTELIGENTE: Orquesta el pipeline completo de generacion de video usando IA.
    
    RELACION CON IA:
    - IA_Clase_03 (Agentes Inteligentes): Este endpoint es un agente que:
      * PERCIBE: Recibe PDF y entrada del usuario
      * DECIDE: Determina que servicios de IA llamar y en que orden
      * ACTUA: Ejecuta el pipeline completo
      * LOGRA OBJETIVO: Retorna video completo con audio
    
    - IA_Clase_04 (Tipos de Agentes): Es un agente REACTIVO que responde a peticiones HTTP
    
    FLUJO DEL AGENTE:
    1. Recibe entrada (PDF o texto)
    2. Extrae texto usando NLP + OCR (IA)
    3. Genera guion usando LLM (IA)
    4. Genera audio usando TTS (IA)
    5. Edita video (NO es IA, es procesamiento de video)
    6. Retorna resultados
    """
    try:
        # ====================================================================
        # PASO 1: Guardar PDF localmente (si se proporciono)
        # ====================================================================
        os.makedirs("photos", exist_ok=True)
        base_id = str(uuid.uuid4())
        blob_url = None
        pdf_text = ""
        local_path = None
        if file is not None:
            file_id = f"{base_id}_{file.filename}"
            local_path = os.path.join("photos", file_id)
            with open(local_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        else:
            file_id = base_id

        # ====================================================================
        # PASO 2: Subir PDF a Azure Blob Storage (almacenamiento)
        # ====================================================================
        if local_path:
            try:
                blob_url = await upload_to_blob(local_path, f"files/{file_id}")
            except Exception as e:
                return {"error": f"Failed to upload PDF to blob: {str(e)}", "pdf_name": file_id}

        # ====================================================================
        # PASO 3: EXTRAER TEXTO DEL PDF USANDO NLP + OCR (IA)
        # Relacion: IA_Clase_02, IA_Clase_06
        # ====================================================================
        if local_path:
            # Esta funcion usa procesamiento de lenguaje natural (NLP)
            # Si el PDF esta escaneado, usa OCR (Reconocimiento Optico de Caracteres)
            pdf_text = await asyncio.to_thread(extract_text_from_pdf, local_path)

        # ====================================================================
        # PASO 4: GENERAR GUION USANDO MODELO DE LENGUAJE (LLM) - IA
        # Relacion: IA_Clase_05, IA_Clase_07
        # ====================================================================
        # Esta es una llamada a un MODELO DE LENGUAJE GRANDE (LLM)
        # El modelo GPT procesa el texto del PDF y genera un guion creativo
        script = await asyncio.to_thread(
            generate_short_video_script,
            pdf_text,
            client,
            deployment,
            user_additional_input=user_additional_input
        )
        if not script.strip():
            resp = {"error": "Generated script is empty."}
            if local_path:
                resp.update({"pdf_name": file_id, "blob_url": blob_url})
            else:
                resp.update({"topic": user_additional_input})
            return resp

        # ====================================================================
        # PASO 5: GENERAR AUDIO USANDO TEXT-TO-SPEECH (TTS) - IA
        # Relacion: IA_Clase_02, IA_Clase_05
        # ====================================================================
        # Esta es una llamada a un servicio de TTS (Sintesis de Voz)
        # Convierte el texto del guion en audio de voz humana sintetica
        os.makedirs("output/audio", exist_ok=True)
        audio_path = f"output/audio/{file_id}.mp3"
        audio_path, language = await genTTS.generate_tts(script, gender="male", output_path=audio_path)
        audio_url = await upload_to_blob(audio_path, f"audio/{file_id}_{language}.mp3")

        # ====================================================================
        # PASO 6: CREAR JOB Y RETORNAR INMEDIATAMENTE
        # ====================================================================
        # Para evitar timeout de Render, retornamos inmediatamente
        # y ejecutamos la generacion de video en background
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "status": "processing",
            "message": "🎬 Generando video en background...",
            "created_at": datetime.now().isoformat(),
            "script": script,
            "audio_url": audio_url,
            "video_url": None
        }
        
        # Ejecutar generacion de video en background
        background_tasks.add_task(
            process_video_generation,
            job_id=job_id,
            file_id=file_id,
            local_path=local_path,
            blob_url=blob_url,
            user_additional_input=user_additional_input,
            script=script,
            audio_path=audio_path,
            audio_url=audio_url,
            language=language
        )
        
        # Retornar inmediatamente con job_id y resultados parciales
        result = {
            "job_id": job_id,
            "script": script,
            "audio_url": audio_url,
            "video_url": None,  # Se actualizara cuando termine el background task
            "status": "processing",
            "message": "Video generandose en background. Usa /generate/video/status/{job_id} para verificar el estado."
        }
        if local_path:
            result.update({
                "pdf_name": file_id,
                "pdf_blob_url": blob_url,
            })
        else:
            result.update({
                "topic": user_additional_input
            })
        
        print(f"📤 Retornando resultados inmediatamente (video en background):")
        print(f"   📝 Script length: {len(script)} caracteres")
        print(f"   🎵 Audio URL: {audio_url}")
        print(f"   🆔 Job ID: {job_id}")
        return result

    except Exception as e:
        return {"error": f"Server error: {str(e)}"}

@app.get("/generate/video/status/{job_id}")
async def get_video_status(job_id: str):
    """
    Endpoint para verificar el estado de un job de generacion de video.
    El frontend debe hacer polling a este endpoint cada pocos segundos.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "message": job.get("message", ""),
        "result": job.get("result"),
        "error": job.get("error"),
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at")
    }

@app.get("/generate/video/result/{job_id}")
async def get_video_result(job_id: str):
    """
    Endpoint para obtener los resultados completos de un job.
    Retorna los mismos datos que el endpoint original cuando el video esta listo.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job.get("status") != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not completed yet. Status: {job.get('status')}"
        )
    
    return job.get("result")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)