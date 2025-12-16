# 📚 StudAI - Tecnologías de Inteligencia Artificial Utilizadas

## 🎯 Resumen

StudAI es una aplicación que utiliza tecnologías de Inteligencia Artificial para transformar documentos PDF en videos de formato corto (short-form) listos para compartir en redes sociales. El sistema procesa el contenido de los PDFs, genera scripts optimizados, crea narraciones con voz sintética y produce videos finales.

---

## 🤖 Tecnologías de IA Implementadas

### 1. **Modelos de Lenguaje (LLMs - Large Language Models)**
**Concepto:** Los Modelos de Lenguaje son sistemas de IA entrenados para entender y generar texto de manera similar a como lo haría un humano.

**Uso en StudAI:**
- **Generación de Scripts:** Los modelos de lenguaje analizan el contenido del PDF y generan scripts optimizados para videos cortos
- **Procesamiento de Texto:** Extraen información clave del documento y la transforman en un formato narrativo atractivo
- **Personalización:** Permiten ajustar el tono, estilo y contenido según las preferencias del usuario

**Ubicación en el Frontend:**
```12:14:StudAI-front/lib/api.ts
const ENDPOINT = "http://127.0.0.1:8000/generate/video";
```
El frontend envía el PDF y las instrucciones adicionales del usuario al backend, que utiliza modelos de lenguaje para procesar y generar el script.

**Referencia en el código:**
- `StudAI-front/app/video/page.tsx` - Página principal donde se sube el PDF y se especifican preferencias
- `StudAI-front/lib/api.ts` - Función `generateVideo()` que comunica con el backend
- `StudAI-front/models/input.ts` - Interfaz que incluye `user_additional_input` para personalizar la generación

---

### 2. **Procesamiento de Lenguaje Natural (NLP)**
**Concepto:** El NLP permite a las máquinas entender, interpretar y manipular el lenguaje humano.

**Uso en StudAI:**
- **Extracción de Información:** Analiza el contenido del PDF para identificar conceptos clave, temas principales y puntos importantes
- **Comprensión Semántica:** Entiende el contexto y significado del texto para generar scripts coherentes
- **Análisis de Sentimiento y Tono:** Ajusta el estilo del script según las preferencias del usuario (divertido, serio, educativo, etc.)

**Ubicación en el Frontend:**
```28:35:StudAI-front/app/video/page.tsx
  const loaderMessages = [
    'Uploading file',
    'Reading your PDF',
    'Generating the best script possible',
    'Making it Funny AF',
    'Cooking the perfect TTS',
    'Stitching your video magic',
  ];
```
El frontend muestra mensajes que indican las etapas de procesamiento, incluyendo la lectura del PDF y generación del script.

---

### 3. **Text-to-Speech (TTS) - Síntesis de Voz**
**Concepto:** Tecnología que convierte texto escrito en audio de voz humana sintética.

**Uso en StudAI:**
- **Narración Automática:** Convierte el script generado en audio con voz natural
- **Generación de Audio:** Crea archivos de audio que se sincronizan con el video final
- **Calidad de Voz:** Utiliza modelos avanzados de TTS para producir voces realistas

**Ubicación en el Frontend:**
```102:118:StudAI-front/app/video/output/page.tsx
            <div className="grid md:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.15 }}
                className="bg-black/40 backdrop-blur-md border border-white/10 rounded-3xl p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Volume2 className="w-6 h-6 text-purple-400" />
                  <h3 className="text-lg font-semibold text-white">Audio Track</h3>
                </div>
                <audio
                  controls
                  src={result.audio_url}
                  className="w-full"
                />
              </motion.div>
```
El frontend muestra el audio generado por TTS en la página de resultados.

**Referencia en el código:**
- `StudAI-front/models/video_output.ts` - Define `audio_url` como parte del resultado
- `StudAI-front/app/video/output/page.tsx` - Reproduce el audio generado

---

### 4. **Tokens e Incrustaciones (Embeddings)**
**Concepto:** 
- **Tokens:** Unidades básicas de texto que los modelos procesan (palabras, subpalabras, caracteres)
- **Embeddings:** Representaciones vectoriales del texto que capturan el significado semántico

**Uso en StudAI:**
- **Tokenización:** El backend divide el contenido del PDF en tokens para procesamiento eficiente
- **Embeddings:** Crea representaciones vectoriales del contenido para entender relaciones semánticas
- **Análisis de Contenido:** Utiliza embeddings para identificar temas, conceptos relacionados y estructura del documento

**Ubicación en el Frontend:**
Aunque el procesamiento de tokens y embeddings ocurre principalmente en el backend, el frontend maneja:
- La carga del archivo PDF que será tokenizado
- La recepción del script generado (que fue procesado usando tokens y embeddings)

**Referencia en el código:**
- `StudAI-front/lib/api.ts` - Envía el archivo PDF al backend para procesamiento
- `StudAI-front/components/aceternity/FileUpload.tsx` - Componente que maneja la carga de archivos

---

### 5. **Agentes Inteligentes**
**Concepto:** Sistemas autónomos que perciben su entorno y toman acciones para alcanzar objetivos específicos.

**Uso en StudAI:**
- **Orquestación del Proceso:** El sistema actúa como un agente que coordina múltiples tareas:
  1. Recibe el PDF del usuario
  2. Decide cómo procesarlo
  3. Genera el script apropiado
  4. Crea el audio
  5. Produce el video final
- **Toma de Decisiones:** El agente decide el mejor formato, estilo y estructura para el video basándose en el contenido del PDF

**Ubicación en el Frontend:**
```66:93:StudAI-front/app/video/page.tsx
  const handleGenerate = async () => {
    if (!file) return;
    setIsGenerating(true);
    const payload: Input = {
      files: [file],
      user_additional_input: additionalInput,
    };

    try {
      const apiResult = await generateVideo(payload);

      setShowConfetti(true);
      if (audioRef.current) {
        audioRef.current.play().catch((err) => console.log('Audio error:', err));
      }
      try {
        sessionStorage.setItem('studaiLastResult', JSON.stringify(apiResult));
      } catch (e) {
        console.warn('Failed to store result in sessionStorage', e);
      }
      const encoded = encodeURIComponent(JSON.stringify(apiResult));
      router.push(`/video/output?result=${encoded}`);
      setTimeout(() => setShowConfetti(false), 3000);
    } catch (error) {
      console.error('Failed to generate video:', error);
      setIsGenerating(false);
    }
  };
```
El frontend actúa como interfaz para el agente inteligente, enviando tareas y recibiendo resultados.

---

## 📍 Ubicaciones Específicas en el Frontend

### **Página Principal de Generación**
**Archivo:** `StudAI-front/app/video/page.tsx`
- **Líneas 18-209:** Componente principal que permite subir PDFs y especificar preferencias
- **Línea 146:** Menciona "let AI craft a viral-ready script, TTS, and video"
- **Líneas 28-35:** Mensajes de carga que muestran el proceso de IA

### **API Client**
**Archivo:** `StudAI-front/lib/api.ts`
- **Líneas 1-41:** Función `generateVideo()` que comunica con el backend de IA
- **Línea 5:** Endpoint del backend que procesa con IA
- **Líneas 7-10:** Validación de archivos antes de enviar al procesador de IA

### **Página de Resultados**
**Archivo:** `StudAI-front/app/video/output/page.tsx`
- **Líneas 84-100:** Muestra el script generado por IA
- **Líneas 102-118:** Reproduce el audio generado por TTS
- **Líneas 120-136:** Muestra el video final generado

### **Modelos de Datos**
**Archivo:** `StudAI-front/models/video_output.ts`
- **Líneas 1-7:** Define la estructura del resultado que incluye:
  - `script`: Texto generado por modelos de lenguaje
  - `audio_url`: Audio generado por TTS
  - `video_url`: Video final procesado

**Archivo:** `StudAI-front/models/input.ts`
- **Líneas 1-4:** Define la entrada que incluye:
  - `files`: PDF a procesar
  - `user_additional_input`: Instrucciones para personalizar la generación con IA

### **Página de Inicio**
**Archivo:** `StudAI-front/app/home/page.tsx`
- **Líneas 74-90:** Características que mencionan:
  - "Smart Script" - Scripts generados por IA
  - "Natural TTS" - Text-to-Speech
  - "Auto Video" - Generación automática de video

---

## 🔄 Flujo de Procesamiento con IA

1. **Entrada del Usuario** (`StudAI-front/app/video/page.tsx`)
   - Usuario sube un PDF
   - Usuario proporciona instrucciones adicionales (tono, estilo, palabras clave)

2. **Envío al Backend** (`StudAI-front/lib/api.ts`)
   - El frontend envía el PDF y las instrucciones al backend
   - El backend utiliza modelos de lenguaje para procesar el contenido

3. **Procesamiento con IA (Backend)**
   - **Tokenización:** Divide el PDF en tokens
   - **Embeddings:** Crea representaciones semánticas
   - **Generación de Script:** Modelos de lenguaje generan el script
   - **TTS:** Convierte el script en audio
   - **Generación de Video:** Combina audio, imágenes y texto

4. **Resultado** (`StudAI-front/app/video/output/page.tsx`)
   - El frontend recibe y muestra:
     - Script generado
     - Audio con TTS
     - Video final

---

## 📚 Temas de IA Relacionados (Basados en Diapositivas)

### **Clase 01 - Fundamentos básicos de la Inteligencia Artificial**
- StudAI aplica conceptos fundamentales de IA para procesar y generar contenido

### **Clase 02 - Tópicos y paradigmas de la inteligencia artificial**
- Utiliza paradigmas de procesamiento de lenguaje natural y generación de contenido

### **Clase 03 - Agentes Inteligentes**
- El sistema actúa como un agente que orquesta múltiples tareas de procesamiento

### **Clase 04 - Tipos de Programas de Agentes Inteligentes**
- Implementa un agente reactivo que responde a entradas del usuario (PDFs)

### **Clase 05 - Introducción a Modelos de Lenguaje**
- Utiliza modelos de lenguaje para generar scripts a partir del contenido del PDF

### **Clase 06 - Tokens e incrustaciones**
- El backend tokeniza el contenido del PDF y utiliza embeddings para análisis semántico

### **Clase 07 - Modelos de Lenguaje**
- Aplica modelos de lenguaje avanzados para la generación de texto y procesamiento de documentos

---

## 🛠️ Tecnologías y Herramientas

- **Frontend:** Next.js, React, TypeScript
- **Comunicación:** Axios para llamadas HTTP al backend de IA
- **Backend de IA:** FastAPI (inferido por el endpoint y estructura)
- **Modelos de IA:** Modelos de lenguaje (probablemente GPT, Claude, o similares)
- **TTS:** Servicios de síntesis de voz (probablemente ElevenLabs, Google TTS, o similares)

---

## 📝 Notas Adicionales

- El frontend se comunica con un backend en `http://127.0.0.1:8000` que maneja todo el procesamiento de IA
- El sistema está diseñado para generar contenido viral y optimizado para redes sociales
- La personalización permite ajustar el tono y estilo del contenido generado
- El proceso completo puede tomar varios minutos debido a la complejidad del procesamiento de IA

---

**Última actualización:** Basado en el análisis del código del frontend de StudAI

