# ============================================================================
# EJEMPLO DE USO DEL MODULO DE EVALUACION
# ============================================================================
# Este archivo muestra como usar el modulo de evaluacion para medir
# la calidad de los guiones generados por la IA.
# ============================================================================

from services.evaluacion import EvaluadorGuion, evaluar_guion_rapido
from services.genScript import extract_text_from_pdf, generate_short_video_script, client, deployment


def ejemplo_evaluacion_completa(pdf_path: str):
    """
    Ejemplo completo de como evaluar un guion generado.
    
    Este ejemplo:
    1. Extrae texto del PDF
    2. Genera un guion usando la IA
    3. Define conceptos clave e irrelevantes
    4. Evalua el guion con todas las metricas
    5. Muestra el reporte
    """
    print("=" * 80)
    print("EJEMPLO DE EVALUACION DE GUION GENERADO")
    print("=" * 80)
    
    # Paso 1: Extraer texto del PDF
    print("\n1. Extrayendo texto del PDF...")
    texto_pdf = extract_text_from_pdf(pdf_path)
    print(f"   Texto extraido: {len(texto_pdf)} caracteres")
    
    # Paso 2: Generar guion usando la IA
    print("\n2. Generando guion con IA...")
    guion = generate_short_video_script(texto_pdf, client, deployment)
    print(f"   Guion generado: {len(guion)} caracteres")
    print(f"   Primeras 200 caracteres: {guion[:200]}...")
    
    # Paso 3: Definir conceptos clave (esto normalmente lo haria un experto)
    # Para este ejemplo, extraemos algunos conceptos del texto del PDF
    conceptos_clave = [
        "redes neuronales",
        "aprendizaje automatico",
        "inteligencia artificial",
        "modelo",
        "entrenamiento",
        "algoritmo",
        "datos",
        "prediccion"
    ]
    
    # Conceptos irrelevantes que no deben aparecer
    conceptos_irrelevantes = [
        "bibliografia",
        "referencias",
        "agradecimientos",
        "indice",
        "pie de pagina",
        "copyright",
        "pagina"
    ]
    
    print("\n3. Conceptos clave definidos:", len(conceptos_clave))
    print("   Conceptos irrelevantes definidos:", len(conceptos_irrelevantes))
    
    # Paso 4: Evaluar el guion
    print("\n4. Evaluando guion...")
    resultado = evaluar_guion_rapido(
        guion,
        texto_pdf,
        conceptos_clave,
        conceptos_irrelevantes
    )
    
    # Paso 5: Mostrar resultados
    print("\n" + resultado['reporte'])
    
    # Retornar las metricas para uso posterior
    return resultado['metricas']


def ejemplo_evaluacion_personalizada():
    """
    Ejemplo de como usar el evaluador de forma personalizada.
    """
    # Crear evaluador con conceptos especificos
    conceptos_clave = [
        "redes neuronales",
        "perceptron",
        "backpropagation",
        "gradiente descendente"
    ]
    
    conceptos_irrelevantes = [
        "bibliografia",
        "referencias"
    ]
    
    evaluador = EvaluadorGuion(conceptos_clave, conceptos_irrelevantes)
    
    # Guion de ejemplo
    guion = """
    Las redes neuronales son sistemas de aprendizaje automatico.
    El perceptron es la unidad basica.
    El backpropagation permite entrenar la red.
    """
    
    texto_pdf = """
    Las redes neuronales son sistemas computacionales.
    El perceptron es la unidad basica de procesamiento.
    El algoritmo de backpropagation es fundamental.
    El gradiente descendente es un metodo de optimizacion.
    
    Bibliografia: Smith, J. (2020).
    Referencias: Ver seccion 5.3
    """
    
    # Calcular metricas individuales
    matriz = evaluador.calcular_matriz_confusion(guion, texto_pdf)
    print("Matriz de confusion:", matriz)
    
    # Calcular metricas especificas
    precision = evaluador.calcular_precision(matriz)
    recall = evaluador.calcular_sensibilidad(matriz)
    f1 = evaluador.calcular_f1_score(matriz)
    
    print(f"\nPrecision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1-Score: {f1:.2%}")


if __name__ == "__main__":
    # Ejecutar ejemplo personalizado
    print("Ejemplo 1: Evaluacion personalizada")
    print("-" * 80)
    ejemplo_evaluacion_personalizada()
    
    # Para ejecutar el ejemplo completo, descomenta la siguiente linea:
    # ejemplo_evaluacion_completa("photos/tu_archivo.pdf")

