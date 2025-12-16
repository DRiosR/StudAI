# ============================================================================
# MODULO DE EVALUACION DE METRICAS PARA STUDAI
# ============================================================================
# Este modulo implementa metricas de evaluacion basadas en matriz de confusion
# para medir la calidad del guion generado por la IA.
# 
# RELACION CON IA:
# - IA_Clase_02 (Topicos de IA): Evaluacion de sistemas de IA
# - Las metricas miden el rendimiento del modelo de lenguaje (LLM)
# ============================================================================

from typing import List, Dict, Set, Tuple, Optional
import re
from collections import Counter
import os

# Importar matplotlib para graficas (opcional, se maneja si no esta instalado)
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend no interactivo para servidores
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None


class EvaluadorGuion:
    """
    Clase para evaluar la calidad de guiones generados por IA.
    
    Evalua el guion comparandolo con conceptos clave del PDF original
    y calcula metricas basadas en matriz de confusion.
    """
    
    def __init__(self, conceptos_clave: List[str], conceptos_irrelevantes: List[str] = None):
        """
        Inicializa el evaluador con conceptos clave y opcionalmente conceptos irrelevantes.
        
        Parametros:
            conceptos_clave (List[str]): Lista de conceptos importantes que DEBEN aparecer
            conceptos_irrelevantes (List[str]): Lista de conceptos que NO deben aparecer (ruido)
        """
        # Conceptos clave que deben estar en el guion (ground truth)
        self.conceptos_clave = [c.lower().strip() for c in conceptos_clave]
        
        # Conceptos irrelevantes que no deben aparecer (ruido del PDF)
        self.conceptos_irrelevantes = [c.lower().strip() for c in (conceptos_irrelevantes or [])]
    
    def extraer_conceptos_del_guion(self, guion: str) -> Set[str]:
        """
        Extrae conceptos clave del guion generado.
        
        Busca palabras clave y frases que coincidan con los conceptos esperados.
        Usa busqueda flexible para encontrar variaciones de los conceptos.
        
        Parametros:
            guion (str): Texto del guion generado
        
        Retorna:
            Set[str]: Conjunto de conceptos encontrados en el guion
        """
        guion_lower = guion.lower()
        conceptos_encontrados = set()
        
        # Buscar cada concepto clave en el guion
        for concepto in self.conceptos_clave:
            concepto_lower = concepto.lower().strip()
            
            # Metodo 1: Buscar el concepto completo
            if concepto_lower in guion_lower:
                conceptos_encontrados.add(concepto)
                continue
            
            # Metodo 2: Para conceptos largos, buscar palabras clave importantes
            palabras_concepto = concepto_lower.split()
            
            # Filtrar palabras muy comunes (stop words)
            stop_words = {'de', 'la', 'el', 'y', 'a', 'en', 'que', 'es', 'se', 'los', 'las', 'del', 'un', 'una', 'por', 'para', 'con', 'sin', 'sobre', 'entre'}
            palabras_importantes = [p for p in palabras_concepto if p not in stop_words and len(p) > 3]
            
            if len(palabras_importantes) > 0:
                # Si al menos el 50% de las palabras importantes aparecen, considerarlo encontrado
                # (reducido de 70% para ser mas flexible)
                palabras_encontradas = sum(1 for palabra in palabras_importantes if palabra in guion_lower)
                porcentaje_requerido = 0.5 if len(palabras_importantes) > 2 else 0.6  # Mas flexible para conceptos largos
                
                if palabras_encontradas >= len(palabras_importantes) * porcentaje_requerido:
                    conceptos_encontrados.add(concepto)
                    continue
            
            # Metodo 3: Para conceptos muy largos, buscar al menos 2 palabras clave juntas
            if len(palabras_importantes) >= 3:
                # Buscar si al menos 2 palabras importantes aparecen cerca una de otra (dentro de 50 caracteres)
                for i, palabra1 in enumerate(palabras_importantes):
                    for palabra2 in palabras_importantes[i+1:]:
                        if palabra1 in guion_lower and palabra2 in guion_lower:
                            # Verificar que esten cerca
                            idx1 = guion_lower.find(palabra1)
                            idx2 = guion_lower.find(palabra2)
                            if abs(idx1 - idx2) < 100:  # Dentro de 100 caracteres
                                conceptos_encontrados.add(concepto)
                                break
                    if concepto in conceptos_encontrados:
                        break
        
        return conceptos_encontrados
    
    def detectar_alucinaciones(self, guion: str, texto_pdf: str) -> Set[str]:
        """
        Detecta posibles alucinaciones (informacion inventada) en el guion.
        
        Busca frases o conceptos en el guion que no aparecen en el PDF original.
        Esta es una deteccion basica; una implementacion mas sofisticada usaria
        embeddings o modelos de similitud semantica.
        
        Parametros:
            guion (str): Texto del guion generado
            texto_pdf (str): Texto original del PDF
        
        Retorna:
            Set[str]: Conjunto de posibles alucinaciones detectadas
        """
        texto_pdf_lower = texto_pdf.lower()
        guion_lower = guion.lower()
        
        # Filtrar palabras muy comunes que no indican alucinacion
        stop_words = {'que', 'de', 'la', 'el', 'y', 'a', 'en', 'es', 'se', 'los', 'las', 'del', 'un', 'una', 'por', 'para', 'con', 'sin', 'sobre', 'entre', 'como', 'mas', 'muy', 'tan', 'todo', 'todos', 'toda', 'todas', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella', 'aquellos', 'aquellas'}
        
        # Dividir el guion en oraciones
        oraciones_guion = re.split(r'[.!?]\s+', guion_lower)
        alucinaciones = set()
        
        # Para cada oracion del guion, verificar si tiene contenido similar en el PDF
        for oracion in oraciones_guion:
            oracion_clean = oracion.strip()
            if len(oracion_clean) < 15:  # Ignorar oraciones muy cortas
                continue
            
            # Extraer palabras clave de la oracion (palabras de 4+ caracteres, excluyendo stop words)
            palabras_clave = [p for p in re.findall(r'\b\w{4,}\b', oracion_clean) if p not in stop_words]
            
            if len(palabras_clave) >= 2:  # Reducido de 3 a 2 para ser mas estricto
                # Si menos del 20% de las palabras clave aparecen en el PDF, posible alucinacion
                # (reducido de 30% para ser menos estricto - el guion puede parafrasear)
                palabras_en_pdf = sum(1 for palabra in palabras_clave if palabra in texto_pdf_lower)
                porcentaje_coincidencia = palabras_en_pdf / len(palabras_clave) if palabras_clave else 0
                
                # Solo considerar alucinacion si hay muy poca coincidencia
                # El guion puede parafrasear, asi que ser mas flexible
                if porcentaje_coincidencia < 0.2 and len(palabras_clave) >= 4:  # Solo para oraciones con muchas palabras
                    alucinaciones.add(oracion_clean[:100])  # Guardar primeros 100 caracteres
        
        return alucinaciones
    
    def calcular_matriz_confusion(self, guion: str, texto_pdf: str) -> Dict[str, int]:
        """
        Calcula la matriz de confusion para el guion generado.
        
        Parametros:
            guion (str): Texto del guion generado
            texto_pdf (str): Texto original del PDF
        
        Retorna:
            Dict con TP, FP, FN, TN
        """
        # Conceptos encontrados en el guion
        conceptos_encontrados = self.extraer_conceptos_del_guion(guion)
        
        # Verdadero Positivo (TP): Concepto clave que estaba en el PDF y aparecio en el video
        tp = len([c for c in conceptos_encontrados if c in self.conceptos_clave])
        
        # Falso Positivo (FP): Informacion que no estaba en el PDF pero la IA la puso
        # Incluye alucinaciones y conceptos irrelevantes que aparecieron
        alucinaciones = self.detectar_alucinaciones(guion, texto_pdf)
        conceptos_irrelevantes_encontrados = len([c for c in self.conceptos_irrelevantes 
                                                   if c.lower() in guion.lower()])
        fp = len(alucinaciones) + conceptos_irrelevantes_encontrados
        
        # Falso Negativo (FN): Concepto clave que estaba en el PDF pero la IA omitio
        conceptos_perdidos = [c for c in self.conceptos_clave if c not in conceptos_encontrados]
        fn = len(conceptos_perdidos)
        
        # Verdadero Negativo (TN): Informacion irrelevante que la IA correctamente ignoro
        conceptos_irrelevantes_ignorados = len([c for c in self.conceptos_irrelevantes 
                                                  if c.lower() not in guion.lower()])
        tn = conceptos_irrelevantes_ignorados
        
        return {
            'TP': tp,
            'FP': fp,
            'FN': fn,
            'TN': tn
        }
    
    def calcular_exactitud(self, matriz: Dict[str, int]) -> float:
        """
        Calcula la Exactitud (Accuracy).
        
        Mide que tan "limpio y completo" es el guion generado.
        De toda la informacion procesada, que porcentaje fue correctamente
        incluido (lo importante) y correctamente excluido (la basura).
        
        Formula: (TP + TN) / (TP + TN + FP + FN)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: Exactitud entre 0 y 1
        """
        tp = matriz['TP']
        tn = matriz['TN']
        fp = matriz['FP']
        fn = matriz['FN']
        
        total = tp + tn + fp + fn
        if total == 0:
            return 0.0
        
        return (tp + tn) / total
    
    def calcular_sensibilidad(self, matriz: Dict[str, int]) -> float:
        """
        Calcula la Sensibilidad (Recall).
        
        METRICA CRITICA PARA EDUCACION: ¿El video cubrio todos los temas del examen?
        Si el PDF tenia 10 definiciones y el video solo menciono 6, el Recall es 60%.
        
        Formula: TP / (TP + FN)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: Sensibilidad entre 0 y 1
        """
        tp = matriz['TP']
        fn = matriz['FN']
        
        if (tp + fn) == 0:
            return 0.0
        
        return tp / (tp + fn)
    
    def calcular_especificidad(self, matriz: Dict[str, int]) -> float:
        """
        Calcula la Especificidad (Specificity).
        
        ¿Que tan bueno es el sistema ignorando la "paja" (bibliografia, agradecimientos)?
        Mide la capacidad de filtrar el ruido del PDF y no incluirlo en el guion.
        
        Formula: TN / (TN + FP)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: Especificidad entre 0 y 1
        """
        tn = matriz['TN']
        fp = matriz['FP']
        
        if (tn + fp) == 0:
            return 0.0
        
        return tn / (tn + fp)
    
    def calcular_precision(self, matriz: Dict[str, int]) -> float:
        """
        Calcula la Precision.
        
        De todo lo que dice el video, ¿cuanto es realmente cierto y util?
        Si el video dice 5 datos pero 1 es una "alucinacion", la precision baja.
        Una precision alta garantiza que el estudiante no aprendera datos falsos.
        
        Formula: TP / (TP + FP)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: Precision entre 0 y 1
        """
        tp = matriz['TP']
        fp = matriz['FP']
        
        if (tp + fp) == 0:
            return 0.0
        
        return tp / (tp + fp)
    
    def calcular_f1_score(self, matriz: Dict[str, int]) -> float:
        """
        Calcula el Valor F (F1-Score).
        
        Balance perfecto entre no aburrir al alumno (brevedad) y no perder
        informacion (completitud). Un F1-Score de 0.85 significa que resume
        bien sin perder la esencia tecnica del documento.
        
        Formula: 2 * (Precision * Recall) / (Precision + Recall)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: F1-Score entre 0 y 1
        """
        precision = self.calcular_precision(matriz)
        recall = self.calcular_sensibilidad(matriz)
        
        if (precision + recall) == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def calcular_tasa_falsos_positivos(self, matriz: Dict[str, int]) -> float:
        """
        Calcula la Tasa de Falsos Positivos (FPR) - Alucinaciones.
        
        Mide con que frecuencia la IA inventa cosas.
        Quieres que esto sea cercano a 0.
        
        Formula: FP / (FP + TN)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: Tasa de falsos positivos entre 0 y 1
        """
        fp = matriz['FP']
        tn = matriz['TN']
        
        if (fp + tn) == 0:
            return 0.0
        
        return fp / (fp + tn)
    
    def calcular_tasa_falsos_negativos(self, matriz: Dict[str, int]) -> float:
        """
        Calcula la Tasa de Falsos Negativos (FNR) - Omisiones.
        
        Mide con que frecuencia la IA olvida temas importantes.
        
        Formula: FN / (FN + TP)
        
        Parametros:
            matriz (Dict[str, int]): Matriz de confusion
        
        Retorna:
            float: Tasa de falsos negativos entre 0 y 1
        """
        fn = matriz['FN']
        tp = matriz['TP']
        
        if (fn + tp) == 0:
            return 0.0
        
        return fn / (fn + tp)
    
    def evaluar_guion(self, guion: str, texto_pdf: str) -> Dict[str, float]:
        """
        Evalua un guion completo y retorna todas las metricas.
        
        Parametros:
            guion (str): Texto del guion generado
            texto_pdf (str): Texto original del PDF
        
        Retorna:
            Dict con todas las metricas calculadas
        """
        # Calcular matriz de confusion
        matriz = self.calcular_matriz_confusion(guion, texto_pdf)
        
        # Calcular todas las metricas
        metricas = {
            'matriz_confusion': matriz,
            'exactitud': self.calcular_exactitud(matriz),
            'sensibilidad': self.calcular_sensibilidad(matriz),
            'especificidad': self.calcular_especificidad(matriz),
            'precision': self.calcular_precision(matriz),
            'f1_score': self.calcular_f1_score(matriz),
            'tasa_falsos_positivos': self.calcular_tasa_falsos_positivos(matriz),
            'tasa_falsos_negativos': self.calcular_tasa_falsos_negativos(matriz),
        }
        
        return metricas
    
    def generar_reporte(self, metricas: Dict) -> str:
        """
        Genera un reporte legible de las metricas de evaluacion.
        
        Parametros:
            metricas (Dict): Diccionario con las metricas calculadas
        
        Retorna:
            str: Reporte formateado
        """
        matriz = metricas['matriz_confusion']
        
        reporte = f"""
================================================================================
                    REPORTE DE EVALUACION DEL GUION
================================================================================

MATRIZ DE CONFUSION:
  Verdadero Positivo (TP):  {matriz['TP']:3d}  - Conceptos clave incluidos correctamente
  Falso Positivo (FP):      {matriz['FP']:3d}  - Alucinaciones o ruido incluido
  Falso Negativo (FN):      {matriz['FN']:3d}  - Conceptos clave omitidos
  Verdadero Negativo (TN):  {matriz['TN']:3d}  - Ruido correctamente ignorado

METRICAS DE RENDIMIENTO:
  Exactitud (Accuracy):     {metricas['exactitud']:.2%}  - Que tan limpio y completo es el guion
  Sensibilidad (Recall):    {metricas['sensibilidad']:.2%}  - Que tan completo es (CRITICO para educacion)
  Especificidad:            {metricas['especificidad']:.2%}  - Capacidad de filtrar ruido
  Precision:                {metricas['precision']:.2%}  - Que tan cierto es el contenido
  F1-Score:                 {metricas['f1_score']:.2%}  - Balance entre completitud y brevedad

TASAS DE ERROR:
  Tasa Falsos Positivos:    {metricas['tasa_falsos_positivos']:.2%}  - Frecuencia de alucinaciones
  Tasa Falsos Negativos:    {metricas['tasa_falsos_negativos']:.2%}  - Frecuencia de omisiones

INTERPRETACION:
  - Una exactitud del {metricas['exactitud']:.0%} significa que el guion es {'muy fiel' if metricas['exactitud'] > 0.9 else 'moderadamente fiel' if metricas['exactitud'] > 0.7 else 'poco fiel'} al documento original.
  - Un Recall del {metricas['sensibilidad']:.0%} indica que se cubrieron {'todos' if metricas['sensibilidad'] > 0.9 else 'la mayoria' if metricas['sensibilidad'] > 0.7 else 'pocos'} los conceptos clave.
  - Una Precision del {metricas['precision']:.0%} garantiza que {'casi todo' if metricas['precision'] > 0.9 else 'la mayoria' if metricas['precision'] > 0.7 else 'poco'} el contenido es veraz.

================================================================================
"""
        return reporte
    
    def generar_graficas(self, metricas: Dict, output_dir: str = "output/graficas") -> Dict[str, str]:
        """
        Genera graficas visuales de las metricas de evaluacion.
        
        Parametros:
            metricas (Dict): Diccionario con las metricas calculadas
            output_dir (str): Directorio donde guardar las graficas
        
        Retorna:
            Dict[str, str]: Diccionario con nombres de graficas y sus rutas
        """
        if not MATPLOTLIB_AVAILABLE:
            return {}
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        rutas_graficas = {}
        
        try:
            # 1. Matriz de confusion (Heatmap)
            rutas_graficas['matriz_confusion'] = self._grafica_matriz_confusion(
                metricas['matriz_confusion'], output_dir
            )
            
            # 2. Metricas principales (Barras)
            rutas_graficas['metricas_principales'] = self._grafica_metricas_principales(
                metricas, output_dir
            )
            
            # 3. Comparacion de metricas (Radar)
            rutas_graficas['radar_metricas'] = self._grafica_radar_metricas(
                metricas, output_dir
            )
            
            # 4. Distribucion de conceptos (Pie Charts)
            rutas_graficas['distribucion_conceptos'] = self._grafica_distribucion_conceptos(
                metricas['matriz_confusion'], output_dir
            )
            
        except Exception as e:
            print(f"Error al generar graficas: {e}")
            import traceback
            traceback.print_exc()
            return {}
        
        return rutas_graficas
    
    def _grafica_matriz_confusion(self, matriz: Dict[str, int], output_dir: str) -> str:
        """Genera un heatmap de la matriz de confusion."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Crear matriz 2x2 para el heatmap
        data = [
            [matriz['TP'], matriz['FP']],
            [matriz['FN'], matriz['TN']]
        ]
        
        im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=max(matriz.values()) if max(matriz.values()) > 0 else 1)
        
        # Etiquetas
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Positivo', 'Negativo'])
        ax.set_yticklabels(['Positivo', 'Negativo'])
        ax.set_xlabel('Prediccion')
        ax.set_ylabel('Real')
        ax.set_title('Matriz de Confusion')
        
        # Agregar valores en las celdas
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, data[i][j], ha="center", va="center", color="black", fontweight='bold')
        
        # Agregar etiquetas de TP, FP, FN, TN
        ax.text(0, 0, 'TP', ha='left', va='top', transform=ax.transAxes, fontsize=8, color='gray')
        ax.text(1, 0, 'FP', ha='right', va='top', transform=ax.transAxes, fontsize=8, color='gray')
        ax.text(0, 1, 'FN', ha='left', va='bottom', transform=ax.transAxes, fontsize=8, color='gray')
        ax.text(1, 1, 'TN', ha='right', va='bottom', transform=ax.transAxes, fontsize=8, color='gray')
        
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        
        ruta = os.path.join(output_dir, 'matriz_confusion.png')
        plt.savefig(ruta, dpi=150, bbox_inches='tight')
        plt.close()
        
        return ruta
    
    def _grafica_metricas_principales(self, metricas: Dict, output_dir: str) -> str:
        """Genera grafica de barras con las metricas principales."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        nombres = ['Exactitud', 'Sensibilidad', 'Especificidad', 'Precision', 'F1-Score']
        valores = [
            metricas['exactitud'],
            metricas['sensibilidad'],
            metricas['especificidad'],
            metricas['precision'],
            metricas['f1_score']
        ]
        
        # Colores basados en el valor
        colores = []
        for v in valores:
            if v >= 0.7:
                colores.append('#2ecc71')  # Verde
            elif v >= 0.5:
                colores.append('#f39c12')  # Amarillo
            else:
                colores.append('#e74c3c')  # Rojo
        
        bars = ax.bar(nombres, valores, color=colores, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Agregar valores en las barras
        for bar, valor in zip(bars, valores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{valor:.1%}',
                   ha='center', va='bottom', fontweight='bold')
        
        # Lineas de referencia
        ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='70% (Excelente)')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='50% (Bueno)')
        
        ax.set_ylabel('Valor', fontsize=12, fontweight='bold')
        ax.set_title('Metricas de Evaluacion del Guion', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.1)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        
        ruta = os.path.join(output_dir, 'metricas_principales.png')
        plt.savefig(ruta, dpi=150, bbox_inches='tight')
        plt.close()
        
        return ruta
    
    def _grafica_radar_metricas(self, metricas: Dict, output_dir: str) -> str:
        """Genera grafica tipo radar comparando todas las metricas."""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Metricas a mostrar
        categorias = ['Exactitud', 'Sensibilidad', 'Especificidad', 'Precision', 'F1-Score']
        valores = [
            metricas['exactitud'],
            metricas['sensibilidad'],
            metricas['especificidad'],
            metricas['precision'],
            metricas['f1_score']
        ]
        
        # Convertir a radianes para el grafico polar
        angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
        valores += valores[:1]  # Cerrar el circulo
        angulos += angulos[:1]
        
        ax.plot(angulos, valores, 'o-', linewidth=2, label='Metricas', color='#3498db')
        ax.fill(angulos, valores, alpha=0.25, color='#3498db')
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
        ax.grid(True)
        ax.set_title('Comparacion de Metricas (Radar)', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        ruta = os.path.join(output_dir, 'radar_metricas.png')
        plt.savefig(ruta, dpi=150, bbox_inches='tight')
        plt.close()
        
        return ruta
    
    def _grafica_distribucion_conceptos(self, matriz: Dict[str, int], output_dir: str) -> str:
        """Genera graficas de pastel mostrando la distribucion de conceptos."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Grafica 1: Conceptos clave (TP vs FN)
        if matriz['TP'] + matriz['FN'] > 0:
            ax1.pie(
                [matriz['TP'], matriz['FN']],
                labels=['Incluidos (TP)', 'Omitidos (FN)'],
                autopct='%1.1f%%',
                colors=['#2ecc71', '#e74c3c'],
                startangle=90
            )
            ax1.set_title('Conceptos Clave', fontweight='bold')
        
        # Grafica 2: Conceptos irrelevantes (TN vs FP)
        if matriz['TN'] + matriz['FP'] > 0:
            ax2.pie(
                [matriz['TN'], matriz['FP']],
                labels=['Ignorados (TN)', 'Incluidos (FP)'],
                autopct='%1.1f%%',
                colors=['#2ecc71', '#e74c3c'],
                startangle=90
            )
            ax2.set_title('Conceptos Irrelevantes', fontweight='bold')
        
        plt.suptitle('Distribucion de Conceptos', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        ruta = os.path.join(output_dir, 'distribucion_conceptos.png')
        plt.savefig(ruta, dpi=150, bbox_inches='tight')
        plt.close()
        
        return ruta


# ============================================================================
# FUNCIONES AUXILIARES PARA EXTRACCION AUTOMATICA DE CONCEPTOS
# ============================================================================

def extraer_conceptos_clave_automatico(texto_pdf: str, num_conceptos: int = 10) -> List[str]:
    """
    Extrae conceptos clave automaticamente del texto del PDF.
    
    Esta funcion busca palabras y frases importantes que aparecen frecuentemente
    en el texto, excluyendo palabras comunes.
    
    Parametros:
        texto_pdf (str): Texto del PDF
        num_conceptos (int): Numero de conceptos a extraer
    
    Retorna:
        List[str]: Lista de conceptos clave extraidos
    """
    # Palabras comunes a excluir (stop words en espanol e ingles)
    stop_words = {
        'el', 'la', 'los', 'las', 'de', 'del', 'y', 'a', 'en', 'que', 'es', 'se', 'un', 'una',
        'por', 'para', 'con', 'sin', 'sobre', 'entre', 'como', 'mas', 'muy', 'tan', 'todo',
        'todos', 'toda', 'todas', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
        'aquel', 'aquella', 'aquellos', 'aquellas', 'the', 'a', 'an', 'and', 'or', 'but', 'in',
        'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'cannot'
    }
    
    texto_lower = texto_pdf.lower()
    
    # Extraer palabras de 5+ caracteres (mas significativas)
    palabras = re.findall(r'\b\w{5,}\b', texto_lower)
    
    # Filtrar stop words y contar frecuencias
    palabras_filtradas = [p for p in palabras if p not in stop_words]
    contador = Counter(palabras_filtradas)
    
    # Obtener las palabras mas frecuentes
    conceptos = [palabra for palabra, _ in contador.most_common(num_conceptos * 2)]
    
    # Filtrar palabras que aparecen menos de 2 veces (probablemente no son conceptos clave)
    conceptos_filtrados = [c for c in conceptos if contador[c] >= 2]
    
    return conceptos_filtrados[:num_conceptos]


def sugerir_conceptos_clave(texto_pdf: str, guion: str = None) -> Dict[str, List[str]]:
    """
    Sugiere conceptos clave basandose en el texto del PDF y opcionalmente el guion.
    
    Parametros:
        texto_pdf (str): Texto del PDF
        guion (str): Guion generado (opcional)
    
    Retorna:
        Dict con 'sugeridos' (conceptos del PDF) y 'en_guion' (conceptos que aparecen en el guion)
    """
    # Extraer conceptos automaticamente
    conceptos_sugeridos = extraer_conceptos_clave_automatico(texto_pdf, num_conceptos=15)
    
    # Si hay guion, verificar cuales aparecen
    conceptos_en_guion = []
    if guion:
        guion_lower = guion.lower()
        conceptos_en_guion = [c for c in conceptos_sugeridos if c in guion_lower]
    
    return {
        'sugeridos': conceptos_sugeridos,
        'en_guion': conceptos_en_guion
    }


# ============================================================================
# FUNCION DE CONVENIENCIA PARA USO RAPIDO
# ============================================================================

def evaluar_guion_rapido(
    guion: str,
    texto_pdf: str,
    conceptos_clave: List[str],
    conceptos_irrelevantes: List[str] = None,
    generar_graficas: bool = True,
    output_dir_graficas: str = "output/graficas"
) -> Dict:
    """
    Funcion de conveniencia para evaluar un guion rapidamente.
    
    Parametros:
        guion (str): Texto del guion generado
        texto_pdf (str): Texto original del PDF
        conceptos_clave (List[str]): Lista de conceptos importantes
        conceptos_irrelevantes (List[str]): Lista de conceptos irrelevantes (opcional)
        generar_graficas (bool): Si True, genera graficas de las metricas
        output_dir_graficas (str): Directorio donde guardar las graficas
    
    Retorna:
        Dict con todas las metricas, el reporte y las rutas de las graficas
    """
    evaluador = EvaluadorGuion(conceptos_clave, conceptos_irrelevantes)
    metricas = evaluador.evaluar_guion(guion, texto_pdf)
    reporte = evaluador.generar_reporte(metricas)
    
    resultado = {
        'metricas': metricas,
        'reporte': reporte
    }
    
    # Generar graficas si se solicita y matplotlib esta disponible
    if generar_graficas and MATPLOTLIB_AVAILABLE:
        try:
            rutas_graficas = evaluador.generar_graficas(metricas, output_dir_graficas)
            resultado['graficas'] = rutas_graficas
            if rutas_graficas:
                print(f"\n📊 Graficas generadas en: {output_dir_graficas}")
                for nombre, ruta in rutas_graficas.items():
                    print(f"   ✅ {nombre}: {ruta}")
        except Exception as e:
            print(f"⚠️  Error al generar graficas: {e}")
            resultado['graficas'] = {}
    elif generar_graficas and not MATPLOTLIB_AVAILABLE:
        print("\n⚠️  Matplotlib no esta disponible. Instala con: pip install matplotlib numpy")
        resultado['graficas'] = {}
    
    return resultado


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo de uso
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
    
    conceptos_irrelevantes = [
        "bibliografia",
        "referencias",
        "agradecimientos",
        "indice",
        "pie de pagina"
    ]
    
    # Guion de ejemplo (simulado)
    guion_ejemplo = """
    Las redes neuronales son sistemas de aprendizaje automatico.
    El perceptron es la unidad basica de una red neuronal.
    El backpropagation permite entrenar la red ajustando los pesos.
    El gradiente descendente optimiza la funcion de costo.
    """
    
    texto_pdf_ejemplo = """
    Las redes neuronales son sistemas computacionales inspirados en el cerebro.
    El perceptron es la unidad basica de procesamiento.
    El algoritmo de backpropagation es fundamental para el entrenamiento.
    El gradiente descendente es un metodo de optimizacion.
    Funciones de activacion como ReLU son comunes.
    Las capas ocultas procesan informacion intermedia.
    El overfitting es un problema comun.
    La regularizacion ayuda a prevenirlo.
    El dropout es una tecnica de regularizacion.
    Las redes convolucionales usan operaciones de convolucion.
    
    Bibliografia: Smith, J. (2020). Machine Learning.
    Referencias: Ver seccion 5.3
    Agradecimientos: A todos los colaboradores.
    """
    
    resultado = evaluar_guion_rapido(
        guion_ejemplo,
        texto_pdf_ejemplo,
        conceptos_clave,
        conceptos_irrelevantes
    )
    
    print(resultado['reporte'])

