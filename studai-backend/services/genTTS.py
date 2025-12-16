# ============================================================================
# SERVICIO DE TEXT-TO-SPEECH (TTS) USANDO IA
# ============================================================================
# Este archivo implementa TEXT-TO-SPEECH (Sintesis de Voz) usando IA
# RELACION CON IA:
# -  (Topicos de IA): TTS es un topico de procesamiento de lenguaje
# -  (Modelos de Lenguaje): Los modelos neurales generan voz natural
# TECNOLOGIA: Azure Cognitive Services Speech SDK
# - Usa voces neurales (HD) que suenan como voz humana real
# - Detecta automaticamente el idioma del texto
# ============================================================================

# ============================================================================
# IMPORTACIONES
# ============================================================================
import os  # Para acceder a variables de entorno y crear directorios
import random  # Para seleccionar voces aleatoriamente
import asyncio  # Para ejecutar funciones asincronas (async/await)
from typing import Tuple  # Para tipado: indica que una funcion retorna una tupla

# ============================================================================
# CARGA DE VARIABLES DE ENTORNO
# ============================================================================
try:
    # Cargar variables de entorno desde archivo .env
    # Estas variables contienen las claves de API de Azure Cognitive Services
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # Si no se puede cargar dotenv, continuar sin error
    # Las variables de entorno pueden estar configuradas de otra forma
    pass

# ============================================================================
# IMPORTACION DEL SDK DE AZURE COGNITIVE SERVICES
# ============================================================================
# SDK de Azure Cognitive Services para Text-to-Speech
# Esta es la tecnologia de IA que convierte texto en audio de voz
# Relacion: (Topicos de IA), (Modelos de Lenguaje)
import azure.cognitiveservices.speech as speechsdk  # type: ignore

# ============================================================================
# CONFIGURACION DE VOCES DISPONIBLES
# ============================================================================
# Las voces son modelos de IA entrenados para generar voz humana sintetica
# Cada voz tiene un nombre unico que identifica el idioma, region y estilo

# Voces femeninas en ingles (diferentes acentos)
FEMALE_VOICES = ['en-AU-NatashaNeural', 'en-US-JennyNeural', 'en-GB-LibbyNeural']

# Voces masculinas en ingles (diferentes acentos)
MALE_VOICES = ['en-AU-WilliamNeural', 'en-US-GuyNeural', 'en-GB-RyanNeural']

# Voces en espanol (Mexico y Espana)
SPANISH_VOICES = ['es-MX-DaliaNeural', 'es-ES-DarioNeural', 'es-MX-JorgeNeural', 'es-MX-CarlotaNeural', 'es-ES-AlvaroNeural']

# Combinacion de todas las voces (no se usa actualmente)
VOICES = FEMALE_VOICES + MALE_VOICES

# ============================================================================
# CONFIGURACION DE ARCHIVOS Y PATHS
# ============================================================================
FILE_PATH = 'txt/script-en.txt'  # Ruta de archivo de prueba (solo para testing)
DEFAULT_OUTPUT = 'output/audio-en-f.mp3'  # Ruta por defecto para guardar audio

# ============================================================================
# VOCES DE ALTA DEFINICION (HD) PARA INGLES
# ============================================================================
# Estas son voces neurales de alta calidad que suenan mas naturales
# "Dragon HD Latest" es la tecnologia mas avanzada de Azure
EN_US_MALE_HD_VOICE = 'en-US-Andrew:DragonHDLatestNeural'
EN_US_FEMALE_HD_VOICE = 'en-US-Ava:DragonHDLatestNeural'

# ============================================================================
# VOCES MULTILINGUALES ESTANDAR PARA INGLES
# ============================================================================
# Voces que pueden hablar en multiples idiomas
EN_US_MALE_VOICE = 'en-US-AndrewMultilingualNeural'
EN_US_FEMALE_VOICE = 'en-US-AvaMultilingualNeural'
EN_US_VOICES = [EN_US_FEMALE_VOICE]  # Lista de voces preferidas (no se usa)

# ============================================================================
# VOCES PARA ESPANOL (MEXICO)
# ============================================================================
# Voces neurales estandar para espanol
SPANISH_MALE_VOICE = 'es-MX-JorgeNeural'
SPANISH_FEMALE_VOICE = 'es-MX-DaliaMultilingualNeural' 

# Lista de voces preferidas para espanol
# Se selecciona aleatoriamente una de estas cuando se detecta espanol
SPANISH_PREFERRED_VOICES = [SPANISH_MALE_VOICE, SPANISH_FEMALE_VOICE]


def _xml_escape(text: str) -> str:
    """
    Escapa caracteres especiales de XML para que no causen errores en SSML.
    
    SSML (Speech Synthesis Markup Language) es un formato XML, por lo que
    ciertos caracteres como <, >, &, ", ' deben ser escapados.
    
    Parametros:
        text (str): Texto que puede contener caracteres especiales
    
    Retorna:
        str: Texto con caracteres especiales escapados
    """
    return (
        text.replace("&", "&amp;")   # & debe ser &amp;
        .replace("<", "&lt;")         # < debe ser &lt;
        .replace(">", "&gt;")         # > debe ser &gt;
        .replace('"', "&quot;")       # " debe ser &quot;
        .replace("'", "&apos;")       # ' debe ser &apos;
    )


def _build_ssml(voice_name: str, rate: str, text: str) -> str:
    """
    Construye un archivo SSML (Speech Synthesis Markup Language) para TTS.
    
    SSML es un formato XML que permite controlar como se genera la voz:
    - Que voz usar
    - Velocidad de habla (rate)
    - Idioma (xml:lang)
    
    Parametros:
        voice_name (str): Nombre de la voz neural a usar (ej: "en-US-Ava:DragonHDLatestNeural")
        rate (str): Velocidad de habla (ej: "+20%" significa 20% mas rapido)
        text (str): Texto a convertir en voz
    
    Retorna:
        str: Documento SSML completo listo para enviar al servicio de TTS
    """
    # Extraer el locale (idioma-region) del nombre de la voz
    # Ejemplo: "en-US-Ava" -> locale = "en-US"
    locale = voice_name.split("-", 2)
    xml_lang = f"{locale[0]}-{locale[1]}" if len(locale) >= 2 else "en-US"
    
    # Escapar caracteres especiales del texto para XML
    escaped = _xml_escape(text)
    
    # Construir el documento SSML completo
    # SSML permite controlar la voz, velocidad, tono, etc.
    ssml = (
        f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
        f"xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{xml_lang}'>"
        f"<voice name='{voice_name}'>"
        f"<prosody rate='{rate}'>{escaped}</prosody>"  # rate controla la velocidad
        f"</voice>"
        f"</speak>"
    )
    return ssml


def _get_speech_config() -> speechsdk.SpeechConfig:
    """
    Configura el cliente de Azure Cognitive Services Speech.
    
    Esta configuracion es necesaria para usar el servicio de TTS (IA).
    Crea un objeto de configuracion que contiene las credenciales y
    la informacion de conexion al servicio de Azure.
    
    Retorna:
        speechsdk.SpeechConfig: Objeto de configuracion listo para usar con el sintetizador
    
    Lanza:
        RuntimeError: Si no se encuentra la clave de API o la configuracion de region/endpoint
    """
    # Obtener la clave de API desde variables de entorno
    key = os.getenv('TTS_AZURE_RESOURCE_KEY')
    # Obtener la region (ej: "eastus", "westus2")
    region = os.getenv('TTS_AZURE_REGION')
    # Obtener el endpoint completo (URL del servicio)
    endpoint = os.getenv('TTS_AZURE_ENDPOINT')

    # Verificar que la clave de API este configurada
    if not key:
        raise RuntimeError('TTS_AZURE_RESOURCE_KEY is not set')

    # Si se proporciono un endpoint completo, usarlo
    if endpoint:
        # Configuracion usando endpoint (URL completa)
        return speechsdk.SpeechConfig(subscription=key, endpoint=endpoint)
    
    # Si se proporciono una region, usarla
    if region:
        # Configuracion usando region (Azure determina el endpoint automaticamente)
        return speechsdk.SpeechConfig(subscription=key, region=region)
    
    # Si no hay ni endpoint ni region, lanzar error
    raise RuntimeError('Either TTS_AZURE_REGION or TTS_AZURE_ENDPOINT must be set')

async def generate_tts(text: str, gender: str = None, output_path: str = DEFAULT_OUTPUT):
    """
    Genera audio de voz a partir de texto usando TEXT-TO-SPEECH (TTS) con IA.
    
    RELACION CON IA:
    - IA_Clase_02 (Topicos de IA): TTS es una aplicacion de procesamiento de lenguaje
    - IA_Clase_05 (Modelos de Lenguaje): Usa modelos neurales para generar voz natural
    
    TECNOLOGIA: Azure Cognitive Services Speech SDK
    - Convierte texto escrito en audio de voz humana sintetica
    - Usa voces neurales de alta calidad que suenan naturales
    - Detecta automaticamente el idioma y selecciona la voz apropiada
    
    Returns:
        tuple[str, str]: (output_audio_path, normalized_language)
                         normalized_language is 'english' or 'spanish'
    """

    # ========================================================================
    # DETECCION DE IDIOMA USANDO NLP
    # ========================================================================
    # Detectar el idioma del texto usando procesamiento de lenguaje natural
    # Relacion: IA_Clase_02 (Topicos de IA), IA_Clase_06 (Tokens e incrustaciones)
    language = detect_language(text)
    
    # Velocidad de habla por defecto (20% mas rapido que normal)
    rate = '+20%'

    # ========================================================================
    # LIMPIEZA DEL TEXTO
    # ========================================================================
    # Remover etiquetas de idioma ([SP], [EN]) para que TTS no las lea en voz alta
    # Estas etiquetas son solo para indicar el idioma, no son parte del guion
    text = text.replace('[SP]', '').replace('[EN]', '')

    # ========================================================================
    # SELECCION DE VOZ NEURAL BASADA EN IDIOMA
    # ========================================================================
    # Las voces neurales son modelos de IA entrenados para sonar como humanos
    # Se selecciona una voz apropiada para el idioma detectado
    if language == 'spanish':
        print('Spanish detected')
        # Para espanol, usar velocidad ligeramente mas lenta (15% mas rapido)
        rate = '+15%'
        # Seleccionar aleatoriamente una voz espanola neural (modelo de IA)
        voice_name = random.choice(SPANISH_PREFERRED_VOICES)

    else:  # default = English
        print('English detected')
        # Para ingles, usar voces HD (High Definition) de alta calidad
        # Seleccionar aleatoriamente entre voz masculina o femenina HD
        voice_name = random.choice([
            EN_US_MALE_HD_VOICE,
            EN_US_FEMALE_HD_VOICE
        ])

    print(f"Using voice: {voice_name}")

    # ========================================================================
    # PREPARACION DEL DIRECTORIO DE SALIDA
    # ========================================================================
    # Crear el directorio donde se guardara el archivo de audio si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # ========================================================================
    # CONFIGURACION DEL SERVICIO DE TTS DE AZURE (IA)
    # ========================================================================
    # Obtener la configuracion de conexion a Azure Cognitive Services
    speech_config = _get_speech_config()
    
    # Configurar donde se guardara el archivo de audio generado
    audio_config = speechsdk.audio.AudioConfig(filename=output_path)
    
    # Crear el sintetizador: componente de IA que convierte texto a voz
    # Este objeto es el que realmente ejecuta la sintesis de voz
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,  # Configuracion de conexion
        audio_config=audio_config      # Configuracion de salida de audio
    )

    # ========================================================================
    # CONSTRUCCION DE SSML (SPEECH SYNTHESIS MARKUP LANGUAGE)
    # ========================================================================
    # SSML es un formato XML que permite controlar la velocidad, tono y estilo
    # de la voz generada por IA
    ssml = _build_ssml(voice_name=voice_name, rate=rate, text=text)

    # ========================================================================
    # EJECUTAR LA SINTESIS DE VOZ (TTS) - LLAMADA A LA IA
    # ========================================================================
    # Esta es la parte mas importante: el modelo neural procesa el texto
    # y genera audio de voz humana sintetica
    # Como el SDK no es completamente asincrono, ejecutamos en un executor
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,  # Usar el executor por defecto
        lambda: synthesizer.speak_ssml_async(ssml).get()  # Ejecutar la sintesis
    )

    # ========================================================================
    # VERIFICACION DE RESULTADO
    # ========================================================================
    # Verificar que la sintesis fue exitosa
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = ""
        # Si fue cancelada, obtener detalles del error
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            details = f" Cancellation reason: {cancellation_details.reason}. Error details: {cancellation_details.error_details}"
        raise RuntimeError(f"Azure TTS synthesis failed.{details}")

    print(f'✅ Audio saved to {output_path}')
    # Retornar la ruta del archivo de audio y el idioma detectado
    return output_path, language


def detect_language(text: str) -> str:
    """
    Detecta el idioma del texto usando procesamiento de lenguaje natural (NLP).
    
    RELACION CON IA:
    - IA_Clase_02 (Topicos de IA): Deteccion de idioma es parte de NLP
    - IA_Clase_06 (Tokens e incrustaciones): El texto se analiza para detectar patrones
    
    Esta es una forma simple de deteccion basada en etiquetas.
    En produccion, se podria usar un modelo de IA mas sofisticado.
    
    Parametros:
        text (str): Texto del cual detectar el idioma
    
    Retorna:
        str: 'spanish' o 'english' segun el idioma detectado
    """
    # Buscar la etiqueta [SP] que indica espanol
    if '[SP]' in text:
        return 'spanish'
    
    # Si no hay etiqueta o es ingles, tratar como ingles por defecto
    return 'english'

if __name__ == "__main__":
    with open(FILE_PATH, 'r') as file:
        text = file.read()
    asyncio.run(generate_tts(text, 'male'))
