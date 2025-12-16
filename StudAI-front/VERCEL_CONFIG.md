# Configuracion para Vercel.com (Frontend)

## Configuracion del Proyecto

### Campos a completar en Vercel:

#### **Project Name**
```
stud-ai
```

#### **Framework Preset**
```
Next.js
```
(Vercel detectara automaticamente Next.js)

#### **Root Directory**
```
StudAI-front
```

#### **Build Command**
```
npm run build
```
(Se detecta automaticamente, pero puedes especificarlo)

#### **Output Directory**
```
.next
```
(Se detecta automaticamente para Next.js)

#### **Install Command**
```
npm install
```
(Se detecta automaticamente)

---

## Variables de Entorno

Agrega estas variables de entorno en la seccion "Environment Variables" de Vercel:

### Backend API URL
```
NEXT_PUBLIC_API_URL=https://tu-backend-en-render.onrender.com
```

**IMPORTANTE:** 
- Reemplaza `tu-backend-en-render.onrender.com` con la URL real de tu backend en Render
- Ejemplo: `https://studai-xxxx.onrender.com`
- No incluyas la barra final (`/`) al final de la URL

---

## Instrucciones paso a paso

1. **Conectar repositorio:**
   - Ve a tu dashboard de Vercel
   - Click en "Add New" > "Project"
   - Selecciona tu repositorio `DRiosR/StudAI` de GitHub

2. **Configurar el proyecto:**
   - **Project Name:** `stud-ai`
   - **Framework Preset:** Next.js (deberia detectarse automaticamente)
   - **Root Directory:** `StudAI-front`
   - Vercel detectara automaticamente Next.js y configurara los comandos

3. **Agregar Variable de Entorno:**
   - Click en "Environment Variables"
   - Agrega:
     - **Key:** `NEXT_PUBLIC_API_URL`
     - **Value:** `https://tu-backend-en-render.onrender.com`
     - **Environment:** Production, Preview, Development (selecciona todos)

4. **Deploy:**
   - Click en "Deploy"
   - Vercel comenzara a construir y desplegar tu aplicacion
   - Espera a que el build termine (puede tardar 2-5 minutos)

5. **Verificar deployment:**
   - Una vez completado, Vercel te dara una URL (ej: `https://stud-ai.vercel.app`)
   - Visita la URL para verificar que funciona

---

## Configuracion adicional

### Actualizar CORS en Backend

Despues de desplegar el frontend, actualiza el CORS en `studai-backend/main.py`:

```python
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://stud-ai.vercel.app",  # Agrega tu dominio de Vercel
    "https://stud-ai-*.vercel.app",  # Para preview deployments
]
```

O mejor aun, usa una variable de entorno:

```python
import os

# Obtener dominio del frontend desde variable de entorno
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    FRONTEND_URL,
]
```

Y agrega en Render:
```
FRONTEND_URL=https://stud-ai.vercel.app
```

---

## Estructura del proyecto

```
StudAI/
├── StudAI-front/          # Frontend (Next.js)
│   ├── app/
│   ├── components/
│   ├── lib/
│   │   └── api.ts         # Usa NEXT_PUBLIC_API_URL
│   └── package.json
└── studai-backend/        # Backend (FastAPI)
    └── main.py
```

---

## Verificacion post-deploy

1. **Verificar que el frontend esta corriendo:**
   - Visita la URL proporcionada por Vercel
   - Deberias ver la pagina principal de StudAI

2. **Verificar conexion con backend:**
   - Intenta subir un PDF y generar un video
   - Revisa la consola del navegador (F12) para ver errores
   - Verifica que las requests van a la URL correcta del backend

3. **Verificar logs:**
   - Ve a la seccion "Deployments" en Vercel
   - Click en el deployment mas reciente
   - Revisa los logs de build y runtime

---

## Troubleshooting

### Error: "Failed to fetch" o CORS
- Verifica que `NEXT_PUBLIC_API_URL` esta configurada correctamente
- Verifica que el backend en Render permite el dominio de Vercel en CORS
- Revisa los logs del backend en Render

### Error: "Module not found"
- Verifica que `package.json` tiene todas las dependencias
- Revisa los logs de build en Vercel

### Error: "Build failed"
- Revisa los logs de build en Vercel
- Verifica que el Root Directory es correcto (`StudAI-front`)
- Verifica que Next.js esta correctamente configurado

### Error: "API Error: Network Error"
- Verifica que el backend en Render esta corriendo
- Verifica que `NEXT_PUBLIC_API_URL` apunta a la URL correcta
- Verifica que no hay problemas de CORS

### Error: "Timeout"
- El procesamiento de video puede tardar mas de 10 minutos
- Considera aumentar el timeout en `lib/api.ts` o implementar polling

---

## Variables de entorno por ambiente

Puedes configurar diferentes valores para diferentes ambientes:

- **Production:** `NEXT_PUBLIC_API_URL=https://studai-prod.onrender.com`
- **Preview:** `NEXT_PUBLIC_API_URL=https://studai-preview.onrender.com`
- **Development:** `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

Vercel permite configurar variables de entorno por ambiente.

---

## Costos

Vercel tiene un plan gratuito (Hobby) que incluye:
- Deployments ilimitados
- 100 GB de ancho de banda
- Builds ilimitados
- Dominio personalizado

Para proyectos mas grandes, considera el plan Pro ($20/mes).

---

## Enlaces utiles

- [Documentacion de Vercel](https://vercel.com/docs)
- [Next.js en Vercel](https://vercel.com/docs/frameworks/nextjs)
- [Variables de entorno en Vercel](https://vercel.com/docs/environment-variables)

---

## Notas importantes

1. **Variables de entorno con `NEXT_PUBLIC_`:**
   - Las variables que empiezan con `NEXT_PUBLIC_` son expuestas al cliente
   - Usa esto para URLs de API que el navegador necesita acceder
   - No uses `NEXT_PUBLIC_` para claves secretas

2. **Build time vs Runtime:**
   - Las variables de entorno se inyectan en build time
   - Si cambias una variable, necesitas hacer un nuevo deploy

3. **Preview deployments:**
   - Vercel crea un deployment para cada PR
   - Puedes usar diferentes URLs de backend para preview vs production

4. **Dominio personalizado:**
   - Puedes agregar un dominio personalizado en la configuracion del proyecto
   - Vercel configurara automaticamente el SSL

