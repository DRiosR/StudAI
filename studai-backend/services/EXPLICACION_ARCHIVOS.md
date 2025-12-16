# Explicacion de los Archivos en la Carpeta Services

Este documento explica que hace cada archivo en la carpeta `services` del backend de StudAI.

---

## ✅ ARCHIVOS USADOS EN PRODUCCION

**Solo estos 3 archivos se usan en el codigo de produccion (`main.py`):**

1. ✅ **`genScript.py`** - Generacion de Guiones usando IA
2. ✅ **`genTTS.py`** - Generacion de Audio usando Text-to-Speech
3. ✅ **`videoEditor.py`** - Edicion de Video

**Evidencia en `main.py`:**
```python
from services.genScript import extract_text_from_pdf, generate_short_video_script, client, deployment
from services import genTTS, videoEditor
```

---

## 📁 Archivos Principales (Usados en Produccion)

### 1. **`genScript.py`** - Generacion de Guiones usando IA

**¿Que hace?**
Este archivo se encarga de extraer texto de PDFs y generar guiones de video usando un Modelo de Lenguaje (LLM).

**Funciones principales:**

#### `extract_text_from_pdf(pdf_path: str) -> str`
- **Proposito**: Extrae texto de un archivo PDF
- **Tecnologias de IA usadas**:
  - **NLP (Procesamiento de Lenguaje Natural)**: Extrae texto de PDFs normales
  - **OCR (Reconocimiento Optico de Caracteres)**: Si el PDF esta escaneado, convierte cada pagina en imagen y usa Tesseract OCR para reconocer el texto
- **Relacion con diapositivas**: IA_Clase_01, IA_Clase_02, IA_Clase_06
- **Como funciona**:
  1. Intenta extraer texto directamente del PDF (si tiene texto seleccionable)
  2. Si el texto esta vacio o parece codificado, usa OCR como fallback
  3. Convierte cada pagina a imagen y usa Tesseract para reconocer texto
  4. Retorna todo el texto extraido

#### `generate_short_video_script(pdf_text: str, ...) -> str`
- **Proposito**: Genera un guion de video corto usando un Modelo de Lenguaje Grande (LLM)
- **Tecnologias de IA usadas**:
  - **LLM (Modelo de Lenguaje)**: Azure OpenAI GPT (modelo `gpt-5-mini`)
  - **Tokens e Incrustaciones**: El texto se convierte en tokens que el modelo procesa
- **Relacion con diapositivas**: IA_Clase_05, IA_Clase_06, IA_Clase_07
- **Como funciona**:
  1. Trunca el texto del PDF a 15000 caracteres (limite de tokens)
  2. Construye un prompt con instrucciones para el modelo
  3. Envia el prompt al modelo GPT usando el patron de "chat completions"
  4. El modelo genera un guion creativo basado en el texto del PDF
  5. Retorna el guion generado

**Flujo completo:**
```
PDF → Extraer texto (NLP/OCR) → Generar guion (LLM) → Retornar guion
```

---

### 2. **`genTTS.py`** - Generacion de Audio usando Text-to-Speech

**¿Que hace?**
Este archivo convierte texto escrito en audio de voz humana sintetica usando Text-to-Speech (TTS).

**Funciones principales:**

#### `generate_tts(text: str, ...) -> tuple[str, str]`
- **Proposito**: Genera audio de voz a partir de texto usando TTS
- **Tecnologias de IA usadas**:
  - **TTS (Text-to-Speech)**: Azure Cognitive Services Speech SDK
  - **Voces Neurales**: Modelos de IA entrenados para sonar como voz humana real
  - **NLP**: Detecta el idioma del texto automaticamente
- **Relacion con diapositivas**: IA_Clase_02, IA_Clase_05
- **Como funciona**:
  1. Detecta el idioma del texto (espanol o ingles)
  2. Selecciona una voz neural apropiada para ese idioma
  3. Construye un archivo SSML (Speech Synthesis Markup Language) con el texto
  4. Envia el SSML al servicio de TTS de Azure
  5. El modelo neural genera audio de voz humana sintetica
  6. Guarda el audio en un archivo MP3
  7. Retorna la ruta del archivo y el idioma detectado

#### `detect_language(text: str) -> str`
- **Proposito**: Detecta el idioma del texto
- **Tecnologias de IA usadas**: NLP basico (deteccion por etiquetas)
- **Relacion con diapositivas**: IA_Clase_02, IA_Clase_06
- **Como funciona**: Busca etiquetas `[SP]` o `[EN]` en el texto para determinar el idioma

**Flujo completo:**
```
Texto → Detectar idioma (NLP) → Seleccionar voz neural → Generar audio (TTS) → Retornar archivo MP3
```

---

### 3. **`videoEditor.py`** - Edicion de Video y Transcripcion de Audio

**¿Que hace?**
Este archivo edita videos (cortar, recortar, sincronizar audio) y puede transcribir audio a texto (aunque actualmente no se usa en el flujo principal).

**Funciones principales:**

#### `videoEditor(video_path: str, audio_path: str, ...) -> str`
- **Proposito**: Edita un video base combinandolo con audio generado
- **Tecnologias usadas**: 
  - **MoviePy**: Biblioteca de Python para edicion de video (NO es IA, es procesamiento de video normal)
- **Como funciona**:
  1. Carga el video base y el audio generado
  2. Corta un segmento aleatorio del video que coincida con la duracion del audio
  3. Recorta el video a formato vertical (9:16) para redes sociales
  4. Sincroniza el audio con el video
  5. Exporta el video final como MP4
  6. Retorna la ruta del video editado

**Funciones auxiliares (NO son IA):**
- `base_edit_export()`: Exporta video con recorte vertical y audio sincronizado
- `extract_random_video_clip()`: Extrae un segmento aleatorio del video
- `crop_to_vertical()`: Recorta el video a formato vertical 9:16

#### `transcribe_audio(audio_path: str, language: str) -> tuple[str, list]`
- **Proposito**: Transcribe audio hablado a texto usando Speech-to-Text (STT)
- **Tecnologias de IA usadas**:
  - **STT (Speech-to-Text)**: AssemblyAI
  - **Modelos Neurales**: Reconocen palabras en audio y generan texto transcrito
- **Relacion con diapositivas**: IA_Clase_02, IA_Clase_05
- **Como funciona**:
  1. Envia el archivo de audio a AssemblyAI
  2. El modelo neural de AssemblyAI procesa el audio
  3. Genera texto transcrito con timestamps a nivel de palabra
  4. Retorna el texto completo y una lista de palabras con sus tiempos
- **NOTA IMPORTANTE**: Esta funcion esta implementada pero **NO se usa actualmente** en el flujo principal. Si se quisiera agregar subtitulos al video, se llamaria esta funcion.

**Funciones auxiliares para subtitulos (NO son IA, solo procesamiento de archivos):**
- `create_srt()`: Crea un archivo SRT (subtitulos) a partir de palabras con timestamps
- `convert_srt_to_ass()`: Convierte archivo SRT a formato ASS (para quemar subtitulos en el video)
- `burn_subtitles_ffmpeg()`: Quema subtitulos en el video usando FFmpeg (NO es IA)

**Flujo completo:**
```
Video base + Audio → Cortar video → Recortar a vertical → Sincronizar audio → Exportar MP4
```

---

## ❌ ARCHIVOS NO USADOS EN PRODUCCION

Estos archivos NO se importan ni se usan en `main.py`:

---

## 📁 Archivos Secundarios (No usados en produccion)

### 4. **`AssemblyAI.py`** - Ejemplo de uso de AssemblyAI

**¿Que hace?**
Este archivo contiene un ejemplo de como usar AssemblyAI directamente con requests HTTP (sin usar el SDK).

**Proposito**: Es un archivo de referencia/ejemplo que muestra:
1. Como subir un archivo de audio a AssemblyAI
2. Como iniciar una tarea de transcripcion
3. Como consultar el estado de la transcripcion
4. Como obtener los resultados con timestamps de palabras

**Estado**: ❌ **NO se usa en produccion**
- NO se importa en `main.py`
- Es solo un archivo de referencia/ejemplo
- El codigo principal usa el SDK de AssemblyAI directamente en `videoEditor.py` (aunque la funcion `transcribe_audio` tampoco se usa actualmente)

---

### 5. **`test.py`** - Archivo de Pruebas

**¿Que hace?**
Este archivo contiene una funcion de prueba que ejecuta todo el pipeline completo de generacion de video.

**Proposito**: Permite probar el sistema completo sin necesidad del servidor web:
1. Extrae texto de un PDF
2. Genera un guion usando el LLM
3. Genera audio usando TTS
4. Edita el video combinando video base + audio
5. Exporta el video final

**Como usarlo**: Ejecutar `python services/test.py` desde la carpeta del backend.

**Estado**: ❌ **NO se usa en produccion**
- NO se importa en `main.py`
- Es solo para pruebas y desarrollo
- Permite probar el pipeline completo sin el servidor web

---

### 6. **`genScript_correct.py`** - Archivo de Respaldo

**¿Que hace?**
Este archivo parece estar vacio o ser una version de respaldo de `genScript.py`.

**Estado**: ❌ **NO se usa en produccion**
- NO se importa en `main.py`
- Es un archivo de respaldo o version antigua
- Nota: Hay un archivo `pipeline.py` que importa `genScript_correct`, pero `pipeline.py` tampoco se usa en `main.py`

---

## 🔄 Flujo Completo del Pipeline

Cuando se genera un video, los archivos de `services` se usan en este orden:

```
1. genScript.py
   ├─ extract_text_from_pdf() → Extrae texto del PDF (NLP/OCR)
   └─ generate_short_video_script() → Genera guion (LLM)

2. genTTS.py
   └─ generate_tts() → Genera audio de voz (TTS)

3. videoEditor.py
   └─ videoEditor() → Edita video (MoviePy, NO es IA)
```

**Opcional (no usado actualmente):**
```
4. videoEditor.py
   └─ transcribe_audio() → Transcribe audio a texto (STT)
   └─ create_srt() → Crea archivo de subtitulos
   └─ burn_subtitles_ffmpeg() → Quema subtitulos en el video
```

---

## 📊 Resumen de Tecnologias de IA por Archivo

| Archivo | Tecnologias de IA | No es IA |
|---------|-------------------|----------|
| `genScript.py` | NLP, OCR, LLM (GPT) | - |
| `genTTS.py` | TTS, Voces Neurales, NLP | - |
| `videoEditor.py` | STT (AssemblyAI) | MoviePy, FFmpeg |
| `AssemblyAI.py` | STT (ejemplo) | - |
| `test.py` | - | - (solo pruebas) |
| `genScript_correct.py` | - | - (respaldo) |

---

## 🎯 Relacion con las Diapositivas de IA

| Archivo | Diapositivas Relacionadas |
|---------|---------------------------|
| `genScript.py` | IA_Clase_01, IA_Clase_02, IA_Clase_05, IA_Clase_06, IA_Clase_07 |
| `genTTS.py` | IA_Clase_02, IA_Clase_05, IA_Clase_06 |
| `videoEditor.py` | IA_Clase_02, IA_Clase_05 |

---

## 💡 Conceptos Clave

- **NLP (Procesamiento de Lenguaje Natural)**: Extraccion y analisis de texto
- **OCR (Reconocimiento Optico de Caracteres)**: Reconocimiento de texto en imagenes
- **LLM (Modelo de Lenguaje Grande)**: Generacion de texto usando modelos como GPT
- **TTS (Text-to-Speech)**: Conversion de texto a voz
- **STT (Speech-to-Text)**: Conversion de voz a texto
- **Tokens**: Unidades en que se divide el texto para procesarlo
- **Voces Neurales**: Modelos de IA entrenados para generar voz humana

