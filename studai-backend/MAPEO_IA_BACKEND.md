# Mapeo de Tecnologías de IA en el Backend de StudAI

Este documento mapea las tecnologías de Inteligencia Artificial utilizadas en el backend de StudAI con los temas cubiertos en las diapositivas de IA.

---

## 📚 Temas de las Diapositivas

1. **IA_Clase_01** - Fundamentos básicos de la Inteligencia Artificial
2. **IA_Clase_02** - Tópicos y paradigmas de la inteligencia artificial
3. **IA_Clase_03** - Agentes Inteligentes
4. **IA_Clase_04** - Tipos de Programas de Agentes Inteligentes
5. **IA_Clase_05** - Introducción a Modelos de Lenguaje
6. **IA_Clase_06** - Tokens e incrustaciones
7. **IA_Clase_07** - Modelos de Lenguaje

---

## 🤖 Tecnologías de IA Implementadas

### 1. **Modelos de Lenguaje (LLMs)** 
**Diapositivas relacionadas:** IA_Clase_05, IA_Clase_07

**¿Qué es?** Modelos de lenguaje grandes que pueden generar texto coherente y contextual basado en prompts.

**Dónde se usa en el código:**

#### `studai-backend/services/genScript.py`

```27:31:studai-backend/services/genScript.py
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)
```

```71:127:studai-backend/services/genScript.py
def generate_short_video_script(pdf_text: str, client: AzureOpenAI, deployment: str, user_additional_input: str | None = None) -> str:
    """
    Generate a witty short-form video script (40–75 seconds, ~120–225 words)
    inspired by the given PDF text or a topic override.

    Output must be pure text — formatted like spoken lines, no headers, no bullets,
    no stage directions, no separators, just the script itself.
    """
    print("🖊️ Generating short-form video script...")
    max_prompt_chars = 15000
    truncated = pdf_text[:max_prompt_chars]

    user_instructions = (
        "Write a short, funny, and engaging script for a short-form video (40–75 seconds). "
        "Use natural spoken rhythm with short sentences and line breaks for pacing. "
        "Languague of the script should match the source material language or user preference. "
        "The tone should be clever, informative, and a little dramatic — similar to an AITA or storytelling TikTok. "
        "Aim for 120–225 words (around 3 words per second). "
        "Start with a strong hook in the first 3–5 seconds, include one surprising or humorous twist, "
        "and end with a one-line mic-drop style conclusion. "
        "Do NOT include any formatting, labels, bullet points, or stage directions — just pure script text as if spoken aloud."
    )

    if user_additional_input:
        user_instructions += f" {user_additional_input}."

    user_instructions += (
        "\n\nUse the following source material as inspiration (if relevant), "
        "The language of the script should be the same as the language of the source material. or the language specified in the user_additional_input."
        "And put the languague at the beginning of the script, like this: [SP] or [EN]:"
        "but do not simply summarize it. If it's not relevant, create an original script on the theme.\n\n"
        f"Source excerpt:\n{truncated}"
    )

    messages = [
        {"role": "system", "content": "You are a witty and concise short-form scriptwriter who only outputs spoken text — no notes or structure. If I have provided no soruce material, use the information from user_additional_input to guide the script."},
        {"role": "user", "content": user_instructions},
    ]

    print("🖊️ Sending request to Azure OpenAI...")

    response = client.chat.completions.create(
        messages=messages,
        max_completion_tokens=1500,
        model=deployment,
    )

    script = ""
    try:
        script = response.choices[0].message.content.strip()
    except Exception:
        script = getattr(response.choices[0], "text", "").strip()


    print("First 10 words of generated script:", " ".join(script.split()[:10])) 

    return script
```

**Explicación:** 
- Se utiliza **Azure OpenAI GPT** (modelo `gpt-5-mini`) para generar guiones de video cortos.
- El modelo recibe el texto extraído del PDF y genera un script creativo y entretenido.
- Utiliza el patrón de **chat completions** con mensajes de sistema y usuario para controlar el comportamiento del modelo.

**Llamada desde `main.py`:**

```118:125:studai-backend/main.py
        # --- Step 4: Generate short video script ---
        script = await asyncio.to_thread(
            generate_short_video_script,
            pdf_text,
            client,
            deployment,
            user_additional_input=user_additional_input
        )
```

---

### 2. **Text-to-Speech (TTS) - Síntesis de Voz**
**Diapositivas relacionadas:** IA_Clase_02 (Tópicos de IA), IA_Clase_05 (Modelos de Lenguaje)

**¿Qué es?** Tecnología que convierte texto escrito en audio de voz humana sintética.

**Dónde se usa en el código:**

#### `studai-backend/services/genTTS.py`

```13:13:studai-backend/services/genTTS.py
import azure.cognitiveservices.speech as speechsdk  # type: ignore
```

```71:85:studai-backend/services/genTTS.py
def _get_speech_config() -> speechsdk.SpeechConfig:
    key = os.getenv('TTS_AZURE_RESOURCE_KEY')
    region = os.getenv('TTS_AZURE_REGION')
    endpoint = os.getenv('TTS_AZURE_ENDPOINT')

    if not key:
        raise RuntimeError('TTS_AZURE_RESOURCE_KEY is not set')

    if endpoint:
        # Endpoint form
        return speechsdk.SpeechConfig(subscription=key, endpoint=endpoint)
    if region:
        # Region form
        return speechsdk.SpeechConfig(subscription=key, region=region)
    raise RuntimeError('Either TTS_AZURE_REGION or TTS_AZURE_ENDPOINT must be set')
```

```87:137:studai-backend/services/genTTS.py
async def generate_tts(text: str, gender: str = None, output_path: str = DEFAULT_OUTPUT):
    """Generate speech from text using Azure Cognitive Services TTS.

    Returns:
        tuple[str, str]: (output_audio_path, normalized_language)
                         normalized_language is 'english' or 'spanish'
    """

    language = detect_language(text)
    rate = '+20%'

    # Remove language tags so TTS doesn't read them
    text = text.replace('[SP]', '').replace('[EN]', '')

    if language == 'spanish':
        print('Spanish detected')
        rate = '+15%'
        # Random Spanish voice (no gender)
        voice_name = random.choice(SPANISH_PREFERRED_VOICES)

    else:  # default = English
        print('English detected')
        # Random English HD voice (ignores gender)
        voice_name = random.choice([
            EN_US_MALE_HD_VOICE,
            EN_US_FEMALE_HD_VOICE
        ])

    print(f"Using voice: {voice_name}")


    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    speech_config = _get_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    ssml = _build_ssml(voice_name=voice_name, rate=rate, text=text)

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, lambda: synthesizer.speak_ssml_async(ssml).get())

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = ""
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            details = f" Cancellation reason: {cancellation_details.reason}. Error details: {cancellation_details.error_details}"
        raise RuntimeError(f"Azure TTS synthesis failed.{details}")

    print(f'✅ Audio saved to {output_path}')
    return output_path, language
```

**Explicación:**
- Se utiliza **Azure Cognitive Services Speech SDK** para generar audio a partir del texto del script.
- Utiliza voces neurales (HD) que suenan más naturales.
- Detecta automáticamente el idioma (español o inglés) y selecciona la voz apropiada.
- Utiliza **SSML (Speech Synthesis Markup Language)** para controlar la velocidad y el estilo de la voz.

**Llamada desde `main.py`:**

```134:138:studai-backend/main.py
        # --- Step 5: Generate TTS ---
        os.makedirs("output/audio", exist_ok=True)
        audio_path = f"output/audio/{file_id}.mp3"
        audio_path, language = await genTTS.generate_tts(script, gender="male", output_path=audio_path)
        audio_url = await upload_to_blob(audio_path, f"audio/{file_id}_{language}.mp3")
```

---

### 3. **Procesamiento de Lenguaje Natural (NLP)**
**Diapositivas relacionadas:** IA_Clase_02 (Tópicos de IA), IA_Clase_06 (Tokens e incrustaciones)

**¿Qué es?** Técnicas para procesar, entender y manipular texto en lenguaje natural.

**Dónde se usa en el código:**

#### `studai-backend/services/genScript.py` - Extracción de texto de PDFs

```33:67:studai-backend/services/genScript.py
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using PyPDF2, with OCR fallback for encoded or scanned PDFs."""
    text_parts = []

    try:
        # --- Try normal extraction first ---
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""
                text_parts.append(page_text)
    except FileNotFoundError:
        raise

    text = "\n\n".join(text_parts).strip()

    # --- Detect unreadable or empty text ---
    if not text or re.search(r"/g\d+", text):
        print("⚠️ PDF appears scanned or encoded — using OCR fallback...")
        text = ""
        pdf = fitz.open(pdf_path)
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            # OCR supports both English and Spanish automatically
            page_text = pytesseract.image_to_string(image, lang="eng+spa")
            text += page_text + "\n\n"
        pdf.close()

    return text.strip()
```

**Explicación:**
- Extrae texto de PDFs usando técnicas de NLP.
- Procesa el texto para detectar si es legible o necesita OCR.
- Trunca el texto a 15,000 caracteres antes de enviarlo al modelo de lenguaje.

#### `studai-backend/services/genTTS.py` - Detección de idioma

```140:145:studai-backend/services/genTTS.py
def detect_language(text: str) -> str:
    """Detects language from tags in text; defaults to English if unspecified."""
    if '[SP]' in text:
        return 'spanish'
    # If explicit English tag present or unspecified, treat as English
    return 'english'
```

**Explicación:**
- Detecta el idioma del texto basándose en etiquetas `[SP]` o `[EN]`.
- Esta detección es parte del procesamiento de lenguaje natural.

---

### 4. **OCR (Reconocimiento Óptico de Caracteres)**
**Diapositivas relacionadas:** IA_Clase_02 (Tópicos de IA), IA_Clase_01 (Fundamentos de IA)

**¿Qué es?** Tecnología que reconoce texto en imágenes o documentos escaneados.

**Dónde se usa en el código:**

#### `studai-backend/services/genScript.py`

```10:10:studai-backend/services/genScript.py
import pytesseract
```

```52:65:studai-backend/services/genScript.py
    # --- Detect unreadable or empty text ---
    if not text or re.search(r"/g\d+", text):
        print("⚠️ PDF appears scanned or encoded — using OCR fallback...")
        text = ""
        pdf = fitz.open(pdf_path)
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            # OCR supports both English and Spanish automatically
            page_text = pytesseract.image_to_string(image, lang="eng+spa")
            text += page_text + "\n\n"
        pdf.close()
```

**Explicación:**
- Utiliza **Tesseract OCR** como fallback cuando el PDF está escaneado o codificado.
- Convierte cada página del PDF en una imagen y luego extrae el texto usando OCR.
- Soporta múltiples idiomas (inglés y español).

---

### 5. **Transcripción de Audio (Speech-to-Text)**
**Diapositivas relacionadas:** IA_Clase_02 (Tópicos de IA), IA_Clase_05 (Modelos de Lenguaje)

**¿Qué es?** Tecnología que convierte audio hablado en texto transcrito.

**Dónde se usa en el código:**

#### `studai-backend/services/videoEditor.py`

```7:10:studai-backend/services/videoEditor.py
import assemblyai as aai

# AssemblyAI setup
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
```

```97:142:studai-backend/services/videoEditor.py
def transcribe_audio(audio_path: str, language: str) -> Tuple[str, list]:
    """
    Transcribe audio with AssemblyAI and return full text + word-level info.
    Automatically supports English and Spanish.
    """
    # Check if API key is set
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError("ASSEMBLYAI_API_KEY environment variable is not set")
    
    print(f"   📡 Using AssemblyAI API key: {api_key[:10]}...")
    print(f"   🌐 Language: {language} -> {map_language(language)}")
    print(f"   📁 Audio file: {audio_path}")
    
    language_code = map_language(language)
    transcriber = aai.Transcriber()
    
    print(f"   ⏳ Starting transcription...")
    transcript = transcriber.transcribe(
        audio_path,
        config=aai.TranscriptionConfig(
            language_code=language_code,
            punctuate=True,
            format_text=True,
            speaker_labels=False,
            auto_chapters=False
        )
    )
    
    print(f"   ⏳ Waiting for transcription to complete...")
    # Wait for transcription to complete
    while transcript.status not in ["completed", "error"]:
        import time
        time.sleep(1)
        transcript = transcriber.get_transcript(transcript.id)
        if transcript.status == "processing":
            print(f"   ⏳ Still processing...")
    
    if transcript.status == "error":
        error_msg = getattr(transcript, 'error', 'Unknown error')
        raise Exception(f"Transcription failed: {error_msg}")

    text = transcript.text or ""
    words = [{"start": w.start, "end": w.end, "text": w.text} for w in (transcript.words or [])]
    print(f"   ✅ Transcription completed: {len(text)} characters, {len(words)} words")
    return text, words
```

**Explicación:**
- Utiliza **AssemblyAI** para transcribir el audio generado por TTS.
- Obtiene timestamps a nivel de palabra para crear subtítulos sincronizados.
- Actualmente esta función está implementada pero **no se está usando en el flujo principal** del pipeline (el video se genera sin subtítulos quemados).

**Nota:** La función `transcribe_audio` existe pero no se llama desde `videoEditor()` en el flujo actual. Si se quisiera agregar subtítulos, se llamaría esta función.

---

### 6. **Agentes Inteligentes**
**Diapositivas relacionadas:** IA_Clase_03, IA_Clase_04

**¿Qué es?** Un agente inteligente es un sistema autónomo que percibe su entorno, toma decisiones y ejecuta acciones para lograr objetivos.

**Dónde se usa en el código:**

#### `studai-backend/main.py` - Pipeline Principal

El archivo `main.py` actúa como un **agente inteligente** que orquesta todo el proceso de generación de video:

```87:186:studai-backend/main.py
@app.post("/generate/video")
async def generate_video(file: UploadFile | None = File(None), user_additional_input: str = Form(...)):
    """
    Upload PDF, run script/audio/video pipeline, and return URLs.
    """
    try:
        # --- Step 1: Optionally save PDF locally (if provided) ---
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

        # --- Step 2: Upload PDF to blob (only if provided) ---
        if local_path:
            try:
                blob_url = await upload_to_blob(local_path, f"files/{file_id}")
            except Exception as e:
                return {"error": f"Failed to upload PDF to blob: {str(e)}", "pdf_name": file_id}

        # --- Step 3: Extract text from PDF (only if provided) ---
        if local_path:
            pdf_text = await asyncio.to_thread(extract_text_from_pdf, local_path)

        # --- Step 4: Generate short video script ---
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

        # --- Step 5: Generate TTS ---
        os.makedirs("output/audio", exist_ok=True)
        audio_path = f"output/audio/{file_id}.mp3"
        audio_path, language = await genTTS.generate_tts(script, gender="male", output_path=audio_path)
        audio_url = await upload_to_blob(audio_path, f"audio/{file_id}_{language}.mp3")

        # --- Step 6: Generate final video ---
        print(f"🎬 Step 6: Starting video generation...")
        os.makedirs("output/videos", exist_ok=True)
        os.makedirs("output/temp", exist_ok=True)
        base_video = "assets/content/MC/mc1.mp4"
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
        final_video_burned_path = await asyncio.to_thread(render_video)
        print(f"✅ Video rendered: {final_video_burned_path}")
        
        print(f"⬆️ Uploading video to blob storage...")
        video_url = await upload_to_blob(final_video_burned_path, f"videos/{file_id}_final_video_{language}.mp4")
        print(f"✅ Video uploaded: {video_url}")

        # --- Step 7: Return results ---
        result = {
            "script": script,
            "audio_url": audio_url,
            "video_url": video_url
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
```

**Explicación:**
- El endpoint `/generate/video` actúa como un **agente inteligente** que:
  1. **Percibe** el entorno: Recibe un PDF y entrada del usuario.
  2. **Toma decisiones**: Decide qué servicios llamar y en qué orden.
  3. **Ejecuta acciones**: 
     - Extrae texto del PDF
     - Genera un script usando LLM
     - Genera audio usando TTS
     - Edita el video
     - Sube los archivos a Azure Blob Storage
  4. **Logra el objetivo**: Retorna un video completo con audio sincronizado.

Este es un ejemplo de un **agente reactivo** (según IA_Clase_04) que responde a estímulos (la petición HTTP) ejecutando una secuencia de acciones predefinidas.

---

## 📊 Resumen de Tecnologías de IA por Archivo

| Archivo | Tecnologías de IA | Diapositivas Relacionadas |
|---------|-------------------|---------------------------|
| `services/genScript.py` | LLMs (Azure OpenAI GPT), NLP, OCR (Tesseract) | IA_Clase_05, IA_Clase_07, IA_Clase_02, IA_Clase_06 |
| `services/genTTS.py` | Text-to-Speech (Azure Cognitive Services) | IA_Clase_02, IA_Clase_05 |
| `services/videoEditor.py` | Speech-to-Text (AssemblyAI) | IA_Clase_02, IA_Clase_05 |
| `main.py` | Agente Inteligente (Orquestación) | IA_Clase_03, IA_Clase_04 |

---

## 🔑 Variables de Entorno Necesarias

Para que todas estas tecnologías de IA funcionen, se requieren las siguientes variables de entorno:

- `AZURE_OPENAI_ENDPOINT` - Endpoint de Azure OpenAI
- `AZURE_OPENAI_KEY` - Clave de API de Azure OpenAI
- `AZURE_OPENAI_DEPLOYMENT` - Nombre del modelo desplegado (ej: `gpt-5-mini`)
- `TTS_AZURE_RESOURCE_KEY` - Clave de Azure Cognitive Services Speech
- `TTS_AZURE_REGION` o `TTS_AZURE_ENDPOINT` - Región o endpoint de TTS
- `ASSEMBLYAI_API_KEY` - Clave de API de AssemblyAI (para transcripción)

---

## 🎯 Flujo Completo del Agente Inteligente

```
1. Usuario sube PDF → Agente percibe entrada
2. Extracción de texto (NLP + OCR si es necesario)
3. Generación de script (LLM - Azure OpenAI GPT)
4. Generación de audio (TTS - Azure Cognitive Services)
5. Edición de video (MoviePy - no es IA, pero es parte del pipeline)
6. Transcripción de audio (AssemblyAI - opcional, no se usa actualmente)
7. Subida a Azure Blob Storage
8. Retorno de URLs al usuario → Agente completa objetivo
```

Este flujo demuestra cómo un **agente inteligente** (el backend) integra múltiples tecnologías de IA para lograr un objetivo complejo: generar videos educativos automáticamente a partir de PDFs.

