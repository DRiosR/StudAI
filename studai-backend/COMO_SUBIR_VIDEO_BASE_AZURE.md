# Como Configurar el Video Base

## Problema
Google Drive bloquea descargas directas de archivos grandes (>100MB), por lo que no funciona para el video base.

## Solucion: Usar Supabase Storage (Recomendado)

### Opcion 1: Supabase Storage (Mas Facil)

1. Sube tu video `mc1.mp4` a Supabase Storage en un bucket publico
2. Obtén la URL pública del video (formato: `https://[PROJECT].supabase.co/storage/v1/object/public/[BUCKET]/[FILE]`)
3. Configura en Render:
   ```
   BASE_VIDEO_URL=https://fdfmtjjeylzznldkrqwl.supabase.co/storage/v1/object/public/studia/1216.mp4
   ```
4. Guarda y reinicia el servicio

**Ventajas:**
- ✅ URLs directas y confiables
- ✅ Sin limites de tamano
- ✅ Facil de configurar
- ✅ Sin necesidad de tokens o SAS

---

## Solucion Alternativa: Usar Azure Blob Storage

### Paso 1: Subir el video a Azure Blob Storage

Tienes varias opciones:

#### Opcion A: Usando Azure Portal
1. Ve a tu cuenta de Azure Portal
2. Navega a tu Storage Account (studai)
3. Ve a "Containers" > "videos" (o crea uno nuevo)
4. Click en "Upload" y sube tu archivo `mc1.mp4`
5. Una vez subido, haz click derecho en el archivo > "Generate SAS"
6. Configura:
   - **Permissions**: Read
   - **Expiry**: Una fecha lejana (ej: 2026-12-31)
7. Copia la "Blob SAS URL" completa

#### Opcion B: Usando Azure Storage Explorer
1. Descarga Azure Storage Explorer
2. Conecta tu cuenta de Azure
3. Navega a tu Storage Account > Containers > videos
4. Arrastra el archivo `mc1.mp4` al contenedor
5. Click derecho en el archivo > "Get Shared Access Signature"
6. Configura permisos de lectura y copia la URL

#### Opcion C: Usando Python (si tienes el video local)
```python
from utils.azure_blob import upload_to_blob

# Subir el video
video_path = "assets/content/MC/mc1.mp4"  # Ruta local
blob_name = "mc1.mp4"  # Nombre en el blob
video_url = await upload_to_blob(video_path, blob_name)
print(f"Video URL: {video_url}")
```

### Paso 2: Configurar BASE_VIDEO_URL en Render

1. Ve a tu servicio en Render
2. Settings > Environment Variables
3. Agrega o actualiza:
   ```
   BASE_VIDEO_URL=https://studai.blob.core.windows.net/videos/mc1.mp4?se=2026-12-31T23:59:59Z&sp=r&sv=2025-11-05&sr=b&sig=TU_SIG_AQUI
   ```
   (Reemplaza con la URL SAS completa que obtuviste)

4. Guarda y reinicia el servicio

### Paso 3: Verificar

Despues de configurar, el servicio deberia:
1. Detectar que el video no existe localmente
2. Descargarlo desde Azure Blob Storage
3. Guardarlo en `assets/content/MC/mc1.mp4`
4. Usarlo para generar videos

## Ventajas de Azure Blob Storage

- ✅ Descargas directas confiables
- ✅ Sin limites de tamano
- ✅ URLs SAS con expiracion controlada
- ✅ Mismo servicio que usas para los videos generados
- ✅ Mejor rendimiento

## Nota sobre URLs SAS

Las URLs SAS tienen una fecha de expiracion. Si expiran:
1. Genera una nueva URL SAS desde Azure Portal
2. Actualiza `BASE_VIDEO_URL` en Render
3. Reinicia el servicio

Para URLs permanentes, considera hacer el contenedor publico (solo lectura) o usar una identidad administrada.

