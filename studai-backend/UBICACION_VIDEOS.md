# 📹 Ubicación de Videos Base

## 📍 Dónde Colocar el Video Base

El video base debe estar en la siguiente ubicación:

```
studai-backend/
└── assets/
    └── content/
        └── MC/
            └── mc1.mp4  ← Tu video base aquí
```

**Ruta completa relativa:** `assets/content/MC/mc1.mp4`

**Ruta completa absoluta (ejemplo en Windows):**
```
C:\Users\danie\OneDrive\Escritorio\7_semestre\IA\StudAI\studai-backend\assets\content\MC\mc1.mp4
```

---

## ✅ Características Recomendadas del Video

### Requisitos Mínimos:
- **Formato:** MP4
- **Nombre:** `mc1.mp4` (o cambia la ruta en `main.py` línea 143)
- **Duración:** Mínimo 30-60 segundos (el sistema selecciona segmentos aleatorios)
- **Resolución:** Horizontal (el sistema lo recorta automáticamente a vertical 9:16)

### Recomendaciones:
- **Códec de video:** H.264
- **Códec de audio:** AAC (aunque se reemplazará con el audio generado)
- **FPS:** 30 fps
- **Calidad:** HD (720p o 1080p) para mejor resultado final

---

## 🔍 Verificar que el Video Existe

Ejecuta el script de verificación:

```bash
cd studai-backend
python verificar_video.py
```

Este script te dirá:
- ✅ Si el video existe
- 📁 La ruta exacta donde lo busca
- 📦 El tamaño del archivo
- ⏱️ La duración del video
- 📐 La resolución

---

## 🎬 Cómo Funciona

1. **El sistema carga tu video base** (`mc1.mp4`)
2. **Selecciona un segmento aleatorio** que coincida con la duración del audio generado
3. **Recorta el video a formato vertical** (9:16) para redes sociales
4. **Sincroniza el audio generado** con el video
5. **Agrega subtítulos** sincronizados usando AssemblyAI
6. **Exporta el video final** en `output/videos/`

---

## ⚠️ Solución de Problemas

### Error: "FileNotFoundError: assets/content/MC/mc1.mp4"

**Solución:**
1. Verifica que el archivo existe en la ruta correcta
2. Verifica que el nombre del archivo es exactamente `mc1.mp4` (case-sensitive en Linux/Mac)
3. Ejecuta `python verificar_video.py` para ver la ruta exacta que busca

### Error: "The video is shorter than the audio duration"

**Solución:**
- Tu video base es más corto que el audio generado
- Usa un video más largo (mínimo 60 segundos recomendado)
- O reduce la longitud del script generado

### Error: "The video is too narrow to be cropped to vertical format"

**Solución:**
- Tu video es muy estrecho (probablemente ya es vertical)
- Usa un video horizontal (16:9 o similar)
- El sistema lo recortará automáticamente a vertical (9:16)

---

## 🔄 Usar un Video Diferente

Si quieres usar un video diferente:

1. **Opción 1: Renombrar tu video**
   ```bash
   # Renombra tu video a mc1.mp4
   mv tu_video.mp4 assets/content/MC/mc1.mp4
   ```

2. **Opción 2: Cambiar la ruta en el código**
   
   Edita `studai-backend/main.py` línea 143:
   ```python
   base_video = "assets/content/MC/tu_video.mp4"  # Cambia aquí
   ```

   También necesitas cambiarlo en:
   - `studai-backend/pipeline.py` línea 71
   - `studai-backend/services/videoEditor.py` línea 241 (si usas el test)

---

## 📝 Notas

- El video base se usa como **fondo visual** para todos los videos generados
- El sistema selecciona **segmentos aleatorios** del video, así que cada video tendrá contenido visual diferente
- El audio original del video se **reemplaza** con el audio generado por TTS
- Los **subtítulos se agregan automáticamente** usando AssemblyAI

---

## 🎨 Tipos de Videos Recomendados

Para mejores resultados, usa videos con:
- ✅ Contenido visual interesante (animaciones, gráficos, personas hablando)
- ✅ Colores vibrantes
- ✅ Movimiento constante (no estático)
- ✅ Sin texto importante (se agregarán subtítulos)
- ✅ Sin audio importante (se reemplazará)

Ejemplos de buenos videos base:
- Videos de stock de personas hablando
- Animaciones abstractas
- Gráficos en movimiento
- Videos de fondo con movimiento

---

**¿Necesitas ayuda?** Ejecuta `python verificar_video.py` para diagnosticar problemas.

