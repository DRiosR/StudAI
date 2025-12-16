#!/usr/bin/env python3
# ============================================================================
# SERVICIO DE GENERACION DE GUIONES USANDO IA
# ============================================================================
# Este archivo implementa dos tecnologias de IA:
# 1. PROCESAMIENTO DE LENGUAJE NATURAL (NLP): Extraccion de texto de PDFs
# 2. MODELOS DE LENGUAJE (LLMs): Generacion de guiones usando Azure OpenAI GPT
# ============================================================================

# ============================================================================
# IMPORTACIONES
# ============================================================================
import os  # Para acceder a variables de entorno y operaciones del sistema
import sys  # Para acceso al sistema (no se usa mucho, pero puede ser util)
import argparse  # Para parsear argumentos de linea de comandos (no se usa en produccion)
from openai import AzureOpenAI  # Cliente para Azure OpenAI (Modelo de Lenguaje)
from pypdf import PdfReader  # Biblioteca para leer PDFs (no se usa, se usa PyPDF2)
from dotenv import load_dotenv  # Para cargar variables de entorno desde archivo .env
from PyPDF2 import PdfReader  # Biblioteca para extraer texto de PDFs normales
import fitz  # PyMuPDF - Para convertir paginas de PDF en imagenes (necesario para OCR)
import pytesseract  # OCR (Reconocimiento Optico de Caracteres) - IA_Clase_01, IA_Clase_02
from PIL import Image  # Pillow - Para procesar imagenes (necesario para OCR)
import io  # Para trabajar con datos en memoria (BytesIO)
import re  # Expresiones regulares para detectar patrones en texto

# ============================================================================
# CONFIGURACION DE VARIABLES DE ENTORNO
# ============================================================================
# Cargar variables de entorno desde archivo .env
# Estas variables contienen las claves de API necesarias para los servicios de IA
load_dotenv()

# ============================================================================
# CONFIGURACION DE AZURE OPENAI (MODELO DE LENGUAJE - LLM)
# ============================================================================
# Estas variables configuran la conexion con Azure OpenAI
# Azure OpenAI es el servicio que proporciona el modelo GPT para generar texto

# Endpoint: URL del servicio de Azure OpenAI
# Si no esta definido, usa un valor por defecto 
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://grassyog-resource.cognitiveservices.azure.com/")

# Deployment: Nombre del modelo GPT desplegado en Azure
# Este es el modelo especifico que se usara para generar guiones
deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")  # Nombre del modelo GPT

# Subscription key: Clave de API para autenticarse con Azure OpenAI
# Esta clave se obtiene del portal de Azure
subscription_key = os.environ.get("AZURE_OPENAI_KEY")

# API version: Version de la API de Azure OpenAI a usar
# Diferentes versiones pueden tener diferentes caracteristicas
api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# ============================================================================
# INICIALIZACION DEL CLIENTE DE AZURE OPENAI
# ============================================================================
# Este cliente se usa para hacer peticiones al modelo de lenguaje GPT
# Una vez inicializado, se puede usar para generar texto usando el metodo chat.completions.create()
client = AzureOpenAI(
    api_version=api_version,      # Version de la API
    azure_endpoint=endpoint,      # URL del servicio
    api_key=subscription_key,    # Clave de autenticacion
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrae texto de un archivo PDF usando tecnicas de Procesamiento de Lenguaje Natural (NLP).
    
    - (Topicos): Procesamiento de texto 
    - (Tokens e incrustaciones): El texto extraido se convierte en tokens para el LLM
    - (Fundamentos ): OCR es una aplicacion basica de IA
    
    Si el PDF esta escaneado, usa OCR (Reconocimiento Optico de Caracteres) como fallback.
    OCR es una tecnologia de IA que reconoce texto en imagenes.
    
    Parametros:
        pdf_path (str): Ruta al archivo PDF del cual extraer texto
    
    Retorna:
        str: Texto extraido del PDF, vacio si no se pudo extraer nada
    """
    # Lista para almacenar el texto de cada pagina
    text_parts = []

    # ========================================================================
    # INTENTO 1: EXTRACCION NORMAL DE TEXTO (NLP BASICO)
    # ========================================================================
    # Esto funciona si el PDF tiene texto seleccionable (no esta escaneado)
    # PyPDF2 puede leer directamente el texto del PDF
    try:
        # Abrir el PDF en modo binario (rb = read binary)
        with open(pdf_path, "rb") as f:
            # Crear un lector de PDF usando PyPDF2
            reader = PdfReader(f)
            # Iterar sobre cada pagina del PDF
            for page in reader.pages:
                try:
                    # Intentar extraer el texto de la pagina
                    # Si no hay texto, retorna cadena vacia
                    page_text = page.extract_text() or ""
                except Exception:
                    # Si hay un error al extraer texto de una pagina,
                    # simplemente usar texto vacio para esa pagina
                    page_text = ""
                # Agregar el texto de la pagina a la lista
                text_parts.append(page_text)
    except FileNotFoundError:
        # Si el archivo no existe, lanzar el error hacia arriba
        raise

    # Unir todo el texto de todas las paginas con doble salto de linea
    # y eliminar espacios al inicio y final
    text = "\n\n".join(text_parts).strip()

    # ========================================================================
    # DETECCION INTELIGENTE: VERIFICAR SI EL TEXTO ES VALIDO
    # ========================================================================
    # Si el texto esta vacio o contiene patrones que indican que esta codificado
    # (como "/g123" que es un patron comun en PDFs escaneados),
    # entonces usar OCR como fallback
    if not text or re.search(r"/g\d+", text):
        print("⚠️ PDF appears scanned or encoded — using OCR fallback...")
        
        # ====================================================================
        # INTENTO 2: USAR OCR (RECONOCIMIENTO OPTICO DE CARACTERES) - IA
        # ====================================================================
        # OCR es una tecnologia de IA que reconoce texto en imagenes
        # Relacion: IA_Clase_01 (Fundamentos de IA), IA_Clase_02 (Topicos de IA)
        
        # Reiniciar el texto para empezar desde cero
        text = ""
        
        # Abrir el PDF usando PyMuPDF (fitz)
        pdf = fitz.open(pdf_path)
        
        # Iterar sobre cada pagina del PDF
        for page_num in range(len(pdf)):
            # Cargar la pagina actual
            page = pdf.load_page(page_num)
            
            # Convertir la pagina en un mapa de pixeles (imagen)
            pix = page.get_pixmap()
            
            # Convertir la imagen a bytes en formato PNG
            img_bytes = pix.tobytes("png")
            
            # Crear una imagen PIL desde los bytes en memoria
            image = Image.open(io.BytesIO(img_bytes))
            
            # Tesseract OCR: Reconocimiento de texto en imagenes usando IA
            # lang="eng+spa" significa que soporta ingles y espanol automaticamente
            # El modelo de IA analiza la imagen y reconoce los caracteres
            page_text = pytesseract.image_to_string(image, lang="eng+spa")
            
            # Agregar el texto reconocido al texto total
            text += page_text + "\n\n"
        
        # Cerrar el PDF
        pdf.close()

    # Retornar el texto extraido, eliminando espacios al inicio y final
    return text.strip()



def generate_short_video_script(pdf_text: str, client: AzureOpenAI, deployment: str, user_additional_input: str | None = None) -> str:
    """
    Genera un guion de video corto usando un MODELO DE LENGUAJE (LLM).
    
    RELACION CON IA:
    - IA_Clase_05 (Introduccion a Modelos de Lenguaje): Usa un LLM (GPT) para generar texto
    - IA_Clase_07 (Modelos de Lenguaje): Implementacion practica de un modelo de lenguaje
    - IA_Clase_06 (Tokens e incrustaciones): El texto se convierte en tokens que el modelo procesa
    
    TECNOLOGIA: Azure OpenAI GPT (Modelo de Lenguaje Grande)
    - El modelo recibe el texto del PDF como contexto
    - Genera un guion creativo y entretenido basado en ese contexto
    - Usa el patron de "chat completions" con mensajes de sistema y usuario
    
    Parametros:
        pdf_text (str): Texto extraido del PDF que servira como contexto
        client (AzureOpenAI): Cliente configurado para hacer peticiones a Azure OpenAI
        deployment (str): Nombre del modelo GPT a usar (ej: "gpt-5-mini")
        user_additional_input (str | None): Instrucciones adicionales del usuario (opcional)
    
    Retorna:
        str: Guion de video generado por el modelo de IA
    """
    print("🖊️ Generating short-form video script...")
    
    # ========================================================================
    # PROCESAMIENTO DE TOKENS: LIMITAR EL TEXTO DE ENTRADA
    # ========================================================================
    # Los modelos de lenguaje tienen limites en la cantidad de tokens que pueden procesar
    # Un token es aproximadamente 4 caracteres, pero puede variar
    # Limitar el texto a 15000 caracteres para no exceder los limites del modelo
    # Esto es parte del procesamiento de tokens (IA_Clase_06)
    max_prompt_chars = 15000
    # Truncar el texto del PDF a los primeros 15000 caracteres
    truncated = pdf_text[:max_prompt_chars]

    # ========================================================================
    # CONSTRUCCION DE INSTRUCCIONES PARA EL MODELO
    # ========================================================================
    # Estas instrucciones le dicen al modelo de IA como debe generar el guion
    # El modelo usa estas instrucciones como "reglas" para crear el contenido
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

    # Si el usuario proporciono instrucciones adicionales, agregarlas
    # Estas instrucciones pueden personalizar el estilo, idioma, tono, etc.
    if user_additional_input:
        user_instructions += f" {user_additional_input}."

    # ========================================================================
    # AGREGAR CONTEXTO DEL PDF AL PROMPT
    # ========================================================================
    # El texto del PDF se agrega como contexto para que el modelo sepa
    # sobre que tema debe generar el guion
    # El modelo usara este contexto para crear un guion relevante
    user_instructions += (
        "\n\nUse the following source material as inspiration (if relevant), "
        "The language of the script should be the same as the language of the source material. or the language specified in the user_additional_input."
        "And put the languague at the beginning of the script, like this: [SP] or [EN]:"
        "but do not simply summarize it. If it's not relevant, create an original script on the theme.\n\n"
        f"Source excerpt:\n{truncated}"
    )

    # ========================================================================
    # CONSTRUCCION DEL PROMPT PARA EL MODELO DE LENGUAJE
    # ========================================================================
    # El modelo GPT usa un patron de "chat completions" con dos tipos de mensajes:
    # 1. Mensaje de sistema: Define el "rol" del modelo (como un guionista)
    # 2. Mensaje de usuario: Contiene las instrucciones y el contexto
    messages = [
        {
            "role": "system", 
            "content": "You are a witty and concise short-form scriptwriter who only outputs spoken text — no notes or structure. If I have provided no soruce material, use the information from user_additional_input to guide the script."
        },
        {
            "role": "user", 
            "content": user_instructions
        },
    ]

    print("🖊️ Sending request to Azure OpenAI...")

    # ========================================================================
    # LLAMADA AL MODELO DE LENGUAJE (LLM) - PARTE CENTRAL DE IA
    # ========================================================================
    # Esta es la llamada que realmente usa la IA para generar el guion
    # El modelo procesa los tokens (IA_Clase_06) y genera texto nuevo
    # basado en el contexto y las instrucciones (IA_Clase_05, IA_Clase_07)
    response = client.chat.completions.create(
        messages=messages,                    # Los mensajes con instrucciones y contexto
        max_completion_tokens=1500,          # Limite de tokens de salida (aproximadamente 6000 caracteres)
        model=deployment,                     # Nombre del modelo GPT (ej: gpt-5-mini)
    )

    # ========================================================================
    # EXTRAER EL TEXTO GENERADO POR EL MODELO
    # ========================================================================
    # El modelo retorna una respuesta compleja, necesitamos extraer solo el texto
    script = ""
    try:
        # Intentar obtener el texto desde response.choices[0].message.content
        script = response.choices[0].message.content.strip()
    except Exception:
        # Si falla, intentar obtenerlo desde otro atributo (compatibilidad)
        script = getattr(response.choices[0], "text", "").strip()

    # Mostrar las primeras 10 palabras del guion generado para debugging
    print("First 10 words of generated script:", " ".join(script.split()[:10])) 

    # Retornar el guion completo generado por la IA
    return script

#main

if __name__ == "__main__":
    #pdf
    pdf_path = "photos/Clase_08.pdf"
    user_additional_input = "Haz el video en español, no en inglés. Y usa palabras coloquiales como no mames, o wey, etc."
    pdf_text = extract_text_from_pdf(pdf_path)
    script = generate_short_video_script(pdf_text, client, deployment, user_additional_input)
    print(script)