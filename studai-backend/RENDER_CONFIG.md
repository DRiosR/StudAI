# Configuracion para Render.com

## Configuracion del Web Service

### Campos a completar en Render:

#### **Name**
```
StudAI
```

#### **Root Directory**
```
studai-backend
```

#### **Build Command**
```
pip install -r requirements.txt
```

#### **Start Command**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### **Instance Type**
- **Recomendado para desarrollo/pruebas:** Starter ($7/mes)
- **Recomendado para produccion:** Standard ($25/mes) o superior
- **Nota:** El procesamiento de video requiere recursos, considera Standard o superior

---

## Variables de Entorno

Agrega estas variables de entorno en la seccion "Environment Variables" de Render:

### Azure OpenAI (Generacion de Guiones)
```
AZURE_OPENAI_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
AZURE_OPENAI_KEY=tu-clave-de-api
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Azure Cognitive Services (Text-to-Speech)
```
TTS_AZURE_RESOURCE_KEY=tu-clave-de-recurso
TTS_AZURE_REGION=tu-region (ej: eastus, westus2)
TTS_AZURE_ENDPOINT=https://tu-region.api.cognitive.microsoft.com/
```

### AssemblyAI (Transcripcion de Audio - Opcional)
```
ASSEMBLYAI_API_KEY=tu-clave-de-api
```

### Azure Blob Storage (Almacenamiento)
```
AZURE_BLOB_ACCOUNT_NAME=tu-nombre-de-cuenta
AZURE_BLOB_KEY=tu-clave-de-cuenta
```

### FFmpeg (Procesamiento de Video - Opcional)
```
FFMPEG_PATH=/usr/bin/ffmpeg
```
**Nota:** En Render, FFmpeg puede no estar disponible. Si es necesario, considera usar un buildpack personalizado o instalar en el Build Command.

---

## Instrucciones paso a paso

1. **Crear nuevo Web Service en Render**
   - Ve a tu dashboard de Render
   - Click en "New" > "Web Service"
   - Conecta tu repositorio de GitHub/GitLab

2. **Configurar el servicio:**
   - **Name:** StudAI
   - **Root Directory:** `studai-backend`
   - **Environment:** Python 3
   - **Branch:** main (o tu rama principal)
   - **Region:** Oregon (US West) o la mas cercana a ti

3. **Configurar Build y Start:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Agregar Variables de Entorno:**
   - Click en "Add Environment Variable"
   - Agrega cada una de las variables listadas arriba
   - **IMPORTANTE:** No compartas tus claves de API publicamente

5. **Seleccionar Instance Type:**
   - Para pruebas: Starter ($7/mes)
   - Para produccion: Standard ($25/mes) o superior

6. **Configurar CORS (Opcional):**
   - Si tu frontend esta en otro dominio, actualiza `main.py` para incluir ese dominio en `allow_origins`

7. **Deploy:**
   - Click en "Create Web Service"
   - Render comenzara a construir y desplegar tu aplicacion
   - Espera a que el build termine (puede tardar varios minutos)

---

## Notas importantes

### 1. CORS
El archivo `main.py` actualmente permite solo `localhost:3000`. Si tu frontend esta en otro dominio, actualiza:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tu-frontend-en-render.onrender.com"  # Agrega tu dominio
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)
```

### 2. FFmpeg
FFmpeg puede no estar disponible en Render por defecto. Si necesitas procesamiento de video con subtitulos:

- **Opcion 1:** Instalar FFmpeg en el Build Command:
  ```
  apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
  ```
  (Requiere usar un Dockerfile o buildpack personalizado)

- **Opcion 2:** Usar un servicio externo para procesar video
- **Opcion 3:** Deshabilitar la funcionalidad de subtitulos quemados

### 3. Archivos temporales
Render tiene almacenamiento efimero. Los archivos generados (videos, audios) deben subirse a Azure Blob Storage inmediatamente.

### 4. Timeouts
Render tiene un timeout de 30 segundos para requests HTTP. Si el procesamiento de video tarda mas, considera:
- Usar procesamiento asincrono
- Usar WebSockets para actualizaciones en tiempo real
- Mover el procesamiento a un servicio separado (Worker)

### 5. Recursos
El procesamiento de video requiere:
- Memoria suficiente (minimo 2GB recomendado)
- CPU adecuada (Standard o superior)
- Tiempo de procesamiento (puede tardar varios minutos)

---

## Verificacion post-deploy

1. **Verificar que el servicio esta corriendo:**
   - Ve a la URL proporcionada por Render (ej: `https://studai.onrender.com`)
   - Deberias ver la documentacion de FastAPI en `/docs`

2. **Probar endpoint de salud:**
   ```bash
   curl https://tu-servicio.onrender.com/docs
   ```

3. **Verificar logs:**
   - Ve a la seccion "Logs" en Render
   - Busca errores de importacion o configuracion

4. **Probar generacion de video:**
   - Envia un PDF al endpoint `/generate/video`
   - Verifica que se genera correctamente

---

## Troubleshooting

### Error: "Module not found"
- Verifica que `requirements.txt` incluye todas las dependencias
- Revisa los logs de build para ver que paquetes fallaron

### Error: "Port already in use"
- Asegurate de usar `$PORT` en el Start Command
- Render asigna el puerto automaticamente

### Error: "FFmpeg not found"
- FFmpeg no esta disponible por defecto en Render
- Considera deshabilitar funcionalidad de subtitulos o usar alternativa

### Error: "Timeout"
- El procesamiento de video puede tardar mas de 30 segundos
- Considera usar procesamiento asincrono o aumentar el timeout

### Error: "CORS"
- Actualiza `allow_origins` en `main.py` con tu dominio de frontend

---

## Costos estimados

- **Starter:** $7/mes - 512 MB RAM, 0.5 CPU (pruebas)
- **Standard:** $25/mes - 2 GB RAM, 1 CPU (produccion basica)
- **Pro:** $85/mes - 4 GB RAM, 2 CPU (produccion recomendada)

**Nota:** Los costos de Azure (OpenAI, TTS, Blob Storage) son adicionales y se facturan por uso.

---

## Enlaces utiles

- [Documentacion de Render](https://render.com/docs)
- [FastAPI en Render](https://render.com/docs/deploy-fastapi)
- [Variables de entorno en Render](https://render.com/docs/environment-variables)

