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

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
import os, uuid, shutil, asyncio
import requests
import re
# Importar servicios de IA
from services.genScript import extract_text_from_pdf, generate_short_video_script, client, deployment
from services import genTTS, videoEditor
from utils.azure_blob import upload_to_blob
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pathlib import Path
app = FastAPI()

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
        # Convertir a link de descarga directa
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

async def get_base_video() -> str:
    """
    Obtiene la ruta del video base. Si no existe localmente, lo descarga desde una URL.
    Soporta links de Google Drive y Azure Blob Storage.
    
    Retorna:
        str: Ruta local del video base
    """
    local_video_path = "assets/content/MC/mc1.mp4"
    
    # Si el video existe localmente, usarlo
    if os.path.exists(local_video_path):
        return local_video_path
    
    # Si no existe, intentar descargarlo desde una URL
    video_url = os.getenv("BASE_VIDEO_URL")
    if video_url:
        print(f"📥 Video base no encontrado localmente. Descargando desde URL...")
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(local_video_path), exist_ok=True)
            
            # Si es un link de Google Drive, convertirlo a descarga directa
            if "drive.google.com" in video_url:
                video_url = convert_google_drive_link(video_url)
                print(f"   Link de Google Drive convertido a descarga directa")
            
            # Descargar el video
            print(f"   Descargando desde: {video_url[:80]}...")
            response = requests.get(video_url, stream=True, timeout=600)
            response.raise_for_status()
            
            # Guardar el video
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(local_video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Mostrar cada MB
                                print(f"   Descargado: {percent:.1f}% ({downloaded // (1024*1024)} MB)")
            
            print(f"✅ Video base descargado exitosamente: {local_video_path}")
            return local_video_path
        except Exception as e:
            print(f"⚠️  Error al descargar video base: {e}")
            print(f"   Asegurate de configurar BASE_VIDEO_URL en las variables de entorno")
            raise FileNotFoundError(f"Video base no encontrado y no se pudo descargar. Configura BASE_VIDEO_URL en Render.")
    
    # Si no hay URL configurada, mostrar error claro
    raise FileNotFoundError(
        f"Video base no encontrado en '{local_video_path}'. "
        f"Configura la variable de entorno BASE_VIDEO_URL con la URL del video (Google Drive o Azure Blob Storage)."
    )

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

@app.post("/generate/video")
async def generate_video(file: UploadFile | None = File(None), user_additional_input: str = Form(...)):
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
        # PASO 6: GENERAR VIDEO FINAL (edicion de video - NO es IA)
        # ====================================================================
        # NOTA: La edicion de video NO es IA, es procesamiento de video normal
        # Sin embargo, si se quisiera agregar subtitulos, se usaria
        # transcripcion de audio (STT) que SÍ es IA (videoEditor.transcribe_audio)
        print(f"🎬 Step 6: Starting video generation...")
        os.makedirs("output/videos", exist_ok=True)
        os.makedirs("output/temp", exist_ok=True)
        # Obtener ruta del video base (descargar desde URL si no existe localmente)
        base_video = await get_base_video()
        final_video_path = f"output/videos/{file_id}_final_video_{language}.mp4"
        
        print(f"   📹 Base video: {base_video}")
        print(f"   🎵 Audio path: {audio_path}")
        print(f"   📁 Output path: {final_video_path}")

        def render_video():
            try:
                return videoEditor.videoEditor(base_video, audio_path, language, output_path=final_video_path)
            except Exception as e:
                print(f"❌ Error in videoEditor: {e}")
                import traceback
                traceback.print_exc()
                raise

        print(f"   ⏳ Rendering video (this may take a while)...")
        try:
            final_video_burned_path = await asyncio.to_thread(render_video)
            print(f"✅ Video rendered: {final_video_burned_path}")
            
            print(f"⬆️ Uploading video to blob storage...")
            video_url = await upload_to_blob(final_video_burned_path, f"videos/{file_id}_final_video_{language}.mp4")
            print(f"✅ Video uploaded: {video_url}")
        except Exception as video_error:
            print(f"❌ Error durante generacion de video: {video_error}")
            import traceback
            traceback.print_exc()
            # Si falla el video, retornar solo script y audio
            video_url = None

        # ====================================================================
        # PASO 7: RETORNAR RESULTADOS
        # El agente ha completado su objetivo
        # ====================================================================
        print(f"📤 Retornando resultados:")
        print(f"   📝 Script length: {len(script)} caracteres")
        print(f"   🎵 Audio URL: {audio_url}")
        print(f"   🎬 Video URL: {video_url if video_url else 'None'}")
        
        result = {
            "script": script,
            "audio_url": audio_url,
            "video_url": video_url if video_url else None
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
        return result

    except Exception as e:
        return {"error": f"Server error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)