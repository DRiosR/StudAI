#!/usr/bin/env python3
# ============================================================================
# SCRIPT PARA EVALUAR UN GUION GENERADO
# ============================================================================
# Este script te permite evaluar un guion generado por la IA
# usando las metricas de evaluacion implementadas.
# ============================================================================

import sys
import os

# Agregar el directorio actual al path para importar modulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.evaluacion import evaluar_guion_rapido, sugerir_conceptos_clave, extraer_conceptos_clave_automatico
from services.genScript import extract_text_from_pdf, generate_short_video_script, client, deployment


def main():
    """
    Funcion principal para evaluar un guion.
    
    Uso:
        python evaluar_guion.py [ruta_al_pdf]
    """
    print("=" * 80)
    print("EVALUADOR DE GUIONES - STUDAI")
    print("=" * 80)
    
    # Obtener ruta del PDF desde argumentos o pedirla
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("\nIngresa la ruta al PDF (o presiona Enter para usar ejemplo): ").strip()
        if not pdf_path:
            # Usar ejemplo si no se proporciona ruta
            print("\nUsando ejemplo de evaluacion...")
            ejemplo_rapido()
            return
    
    if not os.path.exists(pdf_path):
        print(f"\n❌ Error: El archivo '{pdf_path}' no existe.")
        return
    
    # Paso 1: Extraer texto del PDF
    print(f"\n📄 Extrayendo texto del PDF: {pdf_path}")
    try:
        texto_pdf = extract_text_from_pdf(pdf_path)
        print(f"   ✅ Texto extraido: {len(texto_pdf)} caracteres")
    except Exception as e:
        print(f"   ❌ Error al extraer texto: {e}")
        return
    
    # Paso 2: Generar guion usando la IA
    print(f"\n🤖 Generando guion con IA...")
    try:
        guion = generate_short_video_script(texto_pdf, client, deployment)
        print(f"   ✅ Guion generado: {len(guion)} caracteres")
        print(f"\n   📝 Primeras 300 caracteres del guion:")
        print(f"   {guion[:300]}...")
    except Exception as e:
        print(f"   ❌ Error al generar guion: {e}")
        return
    
    # Paso 3: Sugerir conceptos clave automaticamente
    print(f"\n📋 CONFIGURACION DE EVALUACION")
    print(f"   Analizando el PDF para sugerir conceptos clave...")
    
    # Extraer conceptos clave automaticamente
    # Para videos de 40-75 segundos, 8-10 conceptos es ideal para metricas realistas
    conceptos_sugeridos = extraer_conceptos_clave_automatico(texto_pdf, num_conceptos=10)
    
    if conceptos_sugeridos:
        print(f"\n   💡 Conceptos clave sugeridos (basados en frecuencia en el PDF):")
        print(f"   Total encontrados: {len(conceptos_sugeridos)}")
        print(f"\n   Lista completa:")
        # Mostrar todos los conceptos, uno por linea para mejor legibilidad
        for i, concepto in enumerate(conceptos_sugeridos, 1):
            print(f"   {i:2d}. {concepto}")
        
        usar_sugeridos = input(f"\n   ¿Usar estos {len(conceptos_sugeridos)} conceptos sugeridos? (s/n): ").strip().lower()
        if usar_sugeridos == 's':
            conceptos_clave = conceptos_sugeridos
            print(f"   ✅ Usando {len(conceptos_clave)} conceptos sugeridos")
        else:
            # Pedir conceptos manualmente
            print(f"\n   Ingresa los conceptos clave separados por comas:")
            print(f"   (Sugerencia: usa conceptos cortos, ej: 'IA' en vez de 'sistemas capaces de realizar tareas que requieren inteligencia humana')")
            conceptos_input = input("   Conceptos clave: ")
            conceptos_clave = [c.strip() for c in conceptos_input.split(",") if c.strip()]
            
            if not conceptos_clave:
                print("   ⚠️  No se ingresaron conceptos. Usando sugeridos...")
                conceptos_clave = conceptos_sugeridos
    else:
        # Si no se pueden extraer, pedir manualmente
        print(f"\n   No se pudieron extraer conceptos automaticamente.")
        conceptos_input = input("   Ingresa los conceptos clave separados por comas: ")
        conceptos_clave = [c.strip() for c in conceptos_input.split(",") if c.strip()]
        
        if not conceptos_clave:
            print("   ⚠️  No se ingresaron conceptos clave. Usando lista por defecto...")
            conceptos_clave = [
                "inteligencia artificial",
                "aprendizaje automatico",
                "modelo",
                "entrenamiento",
                "algoritmo"
            ]
    
    # Conceptos irrelevantes (opcional)
    conceptos_irrelevantes_input = input("\n   Ingresa conceptos irrelevantes separados por comas (opcional, ej: bibliografia, referencias): ")
    conceptos_irrelevantes = [c.strip() for c in conceptos_irrelevantes_input.split(",") if c.strip()]
    
    if not conceptos_irrelevantes:
        conceptos_irrelevantes = [
            "bibliografia",
            "referencias",
            "agradecimientos",
            "indice",
            "pie de pagina",
            "copyright"
        ]
    
    print(f"\n   ✅ Conceptos clave definidos: {len(conceptos_clave)}")
    print(f"   ✅ Conceptos irrelevantes definidos: {len(conceptos_irrelevantes)}")
    
    # Paso 4: Evaluar el guion
    print(f"\n📊 Evaluando guion...")
    try:
        resultado = evaluar_guion_rapido(
            guion,
            texto_pdf,
            conceptos_clave,
            conceptos_irrelevantes,
            generar_graficas=True,  # Generar graficas automaticamente
            output_dir_graficas="output/graficas"
        )
        
        # Mostrar reporte
        print(resultado['reporte'])
        
        # Mostrar informacion de graficas si se generaron
        if 'graficas' in resultado and resultado['graficas']:
            print(f"\n📈 Graficas de evaluacion generadas:")
            for nombre, ruta in resultado['graficas'].items():
                print(f"   📊 {nombre}: {ruta}")
        
        # Opcion para guardar resultados
        guardar = input("\n¿Guardar resultados en archivo? (s/n): ").strip().lower()
        if guardar == 's':
            # Crear nombre base del archivo (sin extension)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = f"evaluacion_{base_name}.txt"
            output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else "."
            
            # Crear directorio para guardar graficas junto con el reporte
            graficas_dir = os.path.join(output_dir, f"graficas_{base_name}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Evaluacion del guion generado de: {pdf_path}\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Guion generado:\n{guion}\n\n")
                f.write(resultado['reporte'])
                
                # Informacion sobre graficas
                if 'graficas' in resultado and resultado['graficas']:
                    f.write("\n\n" + "=" * 80 + "\n")
                    f.write("GRAFICAS GENERADAS\n")
                    f.write("=" * 80 + "\n\n")
                    f.write("Las siguientes graficas se han generado y guardado:\n\n")
                    
                    # Copiar graficas al directorio del reporte
                    import shutil
                    os.makedirs(graficas_dir, exist_ok=True)
                    
                    for nombre, ruta_original in resultado['graficas'].items():
                        if os.path.exists(ruta_original):
                            # Copiar grafica al directorio del reporte
                            nombre_archivo = os.path.basename(ruta_original)
                            ruta_destino = os.path.join(graficas_dir, nombre_archivo)
                            shutil.copy2(ruta_original, ruta_destino)
                            f.write(f"  📊 {nombre.replace('_', ' ').title()}: {ruta_destino}\n")
                    
                    f.write(f"\nTodas las graficas estan en: {graficas_dir}\n")
                else:
                    f.write("\n\nNota: No se generaron graficas (matplotlib no disponible o error)\n")
            
            print(f"   ✅ Resultados guardados en: {output_file}")
            if 'graficas' in resultado and resultado['graficas']:
                print(f"   ✅ Graficas guardadas en: {graficas_dir}")
        
    except Exception as e:
        print(f"   ❌ Error al evaluar: {e}")
        import traceback
        traceback.print_exc()


def ejemplo_rapido():
    """
    Ejecuta un ejemplo rapido sin necesidad de PDF.
    """
    print("\n" + "=" * 80)
    print("EJEMPLO RAPIDO DE EVALUACION")
    print("=" * 80)
    
    # Guion de ejemplo
    guion = """
    Las redes neuronales son sistemas de aprendizaje automatico inspirados en el cerebro.
    El perceptron es la unidad basica de una red neuronal.
    El algoritmo de backpropagation permite entrenar la red ajustando los pesos.
    El gradiente descendente optimiza la funcion de costo durante el entrenamiento.
    """
    
    # Texto del PDF de ejemplo
    texto_pdf = """
    Las redes neuronales son sistemas computacionales inspirados en el cerebro humano.
    El perceptron es la unidad basica de procesamiento en una red neuronal.
    El algoritmo de backpropagation es fundamental para el entrenamiento de redes.
    El gradiente descendente es un metodo de optimizacion usado en machine learning.
    Las funciones de activacion como ReLU son comunes en redes profundas.
    Las capas ocultas procesan informacion intermedia entre entrada y salida.
    El overfitting es un problema comun en machine learning.
    La regularizacion ayuda a prevenir el overfitting.
    El dropout es una tecnica de regularizacion que desactiva neuronas aleatoriamente.
    Las redes convolucionales usan operaciones de convolucion para procesar imagenes.
    
    Bibliografia: Smith, J. (2020). Machine Learning Fundamentals.
    Referencias: Ver seccion 5.3 para mas detalles.
    Agradecimientos: A todos los colaboradores del proyecto.
    Indice: Pagina 1 - Introduccion, Pagina 2 - Conceptos basicos...
    """
    
    # Conceptos clave
    conceptos_clave = [
        "redes neuronales",
        "perceptron",
        "backpropagation",
        "gradiente descendente",
        "funcion de activacion",
        "capa oculta",
        "overfitting",
        "regularizacion",
        "dropout",
        "convolucion"
    ]
    
    # Conceptos irrelevantes
    conceptos_irrelevantes = [
        "bibliografia",
        "referencias",
        "agradecimientos",
        "indice",
        "pie de pagina"
    ]
    
    print("\n📝 Guion de ejemplo:")
    print(guion)
    
    print("\n📊 Evaluando...")
    resultado = evaluar_guion_rapido(
        guion,
        texto_pdf,
        conceptos_clave,
        conceptos_irrelevantes
    )
    
    print(resultado['reporte'])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluacion cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

