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


def _infer_target_script_language(pdf_text: str, user_additional_input: str | None) -> str:
    """
    Decide si el guion debe ir en español, inglés o dejar que el modelo elija (auto).

    Regla principal: el idioma de la PETICIÓN del usuario manda sobre el idioma del PDF.
    Solo si el usuario no escribió nada útil se usa el PDF como pista.
    """
    user = (user_additional_input or "").strip().lower()
    sample = (pdf_text or "")[:12000].lower()
    blob_user = f" {user} "
    blob_pdf = f" {sample} "

    def explicit_spanish(s: str) -> bool:
        return any(
            p in s
            for p in (
                "español",
                "espanol",
                "en español",
                "en espanol",
                "castellano",
                "habla en español",
                "guion en español",
                "video en español",
                "guión en español",
                "guion en espanol",
            )
        )

    def explicit_english(s: str) -> bool:
        return any(
            p in s
            for p in (
                "english",
                "in english",
                "en inglés",
                "en ingles",
                "script in english",
                "video in english",
            )
        )

    # Palabras típicas cuando el usuario escribe la petición en español (aunque el PDF sea inglés)
    SPANISH_USER_WORDS = (
        "que",
        "como",
        "cómo",
        "para",
        "con",
        "una",
        "unos",
        "unas",
        "los",
        "las",
        "más",
        "mas",
        "también",
        "tambien",
        "este",
        "esta",
        "muy",
        "sobre",
        "hacer",
        "haz",
        "usa",
        "quiero",
        "tono",
        "estilo",
        "palabras",
        "palabra",
        "incluye",
        "incluir",
        "explica",
        "breve",
        "corto",
        "divertido",
        "formal",
        "educativo",
        "coloquial",
        "guion",
        "guión",
        "video",
        "nada",
        "algo",
        "así",
        "asi",
    )
    ENGLISH_USER_WORDS = (
        "the",
        "and",
        "with",
        "that",
        "this",
        "from",
        "your",
        "make",
        "please",
        "want",
        "tone",
        "style",
        "keywords",
        "funny",
        "serious",
        "short",
        "include",
        "explain",
        "script",
    )

    if user:
        if explicit_spanish(user) and not explicit_english(user):
            return "spanish"
        if explicit_english(user) and not explicit_spanish(user):
            return "english"
        # Cualquier tilde / ñ en la petición → español (pide en español aunque el PDF sea otro idioma)
        if any(c in user for c in "áéíóúñü¿¡"):
            return "spanish"
        sp_u = sum(blob_user.count(f" {w} ") for w in SPANISH_USER_WORDS)
        en_u = sum(blob_user.count(f" {w} ") for w in ENGLISH_USER_WORDS)
        if len(user) >= 4 and sp_u > en_u:
            return "spanish"
        if len(user) >= 4 and en_u > sp_u:
            return "english"
        # Imperativos / frases muy comunes en español
        if re.search(
            r"\b(hazlo|haz|usa|usar|cuéntame|cuentame|pon|ponme|dime|explicame|explícame)\b",
            user,
        ):
            return "spanish"
        if re.search(r"\b(make|use|tell me|give me|keep it)\b", user) and sp_u == 0:
            return "english"

    # Petición escrita pero empate (poco texto mezclado): no dejar que el PDF pise al usuario
    if user:
        return "auto"

    # Sin texto del usuario: inferir idioma solo del PDF
    if explicit_spanish(sample) and not explicit_english(sample[:800]):
        return "spanish"

    spanish_chars = sum(1 for c in (pdf_text or "")[:8000] if c in "áéíóúñüÁÉÍÓÚÑÜ¿¡")
    sp_pdf = sum(
        blob_pdf.count(f" {w} ")
        for w in (
            "el",
            "la",
            "de",
            "que",
            "los",
            "las",
            "una",
            "con",
            "por",
            "para",
            "como",
            "más",
            "mas",
            "también",
            "tambien",
        )
    )
    if spanish_chars >= 8 or sp_pdf >= 22:
        return "spanish"

    en_pdf = sum(
        blob_pdf.count(f" {w} ")
        for w in (
            "the",
            "and",
            "of",
            "to",
            "in",
            "is",
            "for",
            "that",
            "with",
            "as",
            "on",
            "are",
            "by",
            "from",
        )
    )
    if en_pdf >= 35 and spanish_chars < 4:
        return "english"

    return "auto"


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

    target_lang = _infer_target_script_language(truncated, user_additional_input)

    # ========================================================================
    # CONSTRUCCION DE INSTRUCCIONES PARA EL MODELO
    # ========================================================================
    # Estas instrucciones le dicen al modelo de IA como debe generar el guion
    # El modelo usa estas instrucciones como "reglas" para crear el contenido
    user_instructions = (
        "Write a short-form video script (40–75 seconds). "
        "Aim for 120–225 words (around 3 words per second). "
        "Start with a clear hook/introduction, then explain the key ideas, and end with a concise closing. "
        "IMPORTANT: If the user provides tone/style/keywords/constraints, FOLLOW THEM with highest priority "
        "(including allowing colloquial language or slang if explicitly requested). "
        "Do NOT include bullet points or stage directions — output only spoken script text. "
        "The first line MUST begin with exactly one language tag as specified below, then the script."
    )

    if target_lang == "spanish":
        user_instructions += (
            "\n\nLANGUAGE (mandatory): Write the ENTIRE script in Spanish. "
            "Do not switch to English (except unavoidable proper nouns or acronyms). "
            "The source material and/or user instructions indicate Spanish. "
            "First line MUST start with: [ES]: "
        )
    elif target_lang == "english":
        user_instructions += (
            "\n\nLANGUAGE (mandatory): Write the ENTIRE script in English. "
            "First line MUST start with: [EN]: "
        )
    else:
        user_instructions += (
            "\n\nLANGUAGE (important): The user's instructions below may be in a different language than the PDF. "
            "Write the script in the SAME language as the user's instructions (how they wrote their request). "
            "If the user wrote in Spanish, output fully in Spanish starting with [ES]: even if the PDF is in English. "
            "If the user wrote in English, output fully in English starting with [EN]: even if the PDF is in Spanish. "
            "Only if the user left no instructions, match the dominant language of the source excerpt."
        )

    # Si el usuario proporciono instrucciones adicionales, agregarlas
    # Estas instrucciones pueden personalizar el estilo, idioma, tono, etc.
    if user_additional_input:
        user_instructions += f"\n\nUser instructions (tone, style, keywords):\n{user_additional_input}"

    # ========================================================================
    # AGREGAR CONTEXTO DEL PDF AL PROMPT
    # ========================================================================
    # El texto del PDF se agrega como contexto para que el modelo sepa
    # sobre que tema debe generar el guion
    # El modelo usara este contexto para crear un guion relevante
    user_instructions += (
        "\n\nUse the following source material as inspiration (if relevant). "
        "Do not only summarize it; adapt it for short-form video. "
        "If it is not relevant, create an original script on the theme implied by the user.\n\n"
        f"Source excerpt:\n{truncated}"
    )

    print(f"🌐 Target script language hint for LLM: {target_lang}")

    # ========================================================================
    # CONSTRUCCION DEL PROMPT PARA EL MODELO DE LENGUAJE
    # ========================================================================
    # El modelo GPT usa un patron de "chat completions" con dos tipos de mensajes:
    # 1. Mensaje de sistema: Define el "rol" del modelo (como un guionista)
    # 2. Mensaje de usuario: Contiene las instrucciones y el contexto
    messages = [
        {
            "role": "system",
            "content": (
                "You are a short-form video scriptwriter. "
                "You only output spoken script text (no notes, no structure). "
                "Respect the LANGUAGE rules in the user message; never default to English when Spanish is required. "
                "When user preferences are provided, follow them (tone, style, keywords, slang/colloquialisms)."
            ),
        },
        {"role": "user", "content": user_instructions},
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