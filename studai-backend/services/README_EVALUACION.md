# Modulo de Evaluacion de Metricas para StudAI

Este modulo implementa metricas de evaluacion basadas en matriz de confusion para medir la calidad de los guiones generados por la IA.

## Metricas Implementadas

### 1. Exactitud (Accuracy)
- **Que mide**: Que tan "limpio y completo" es el guion generado
- **Formula**: (TP + TN) / (TP + TN + FP + FN)
- **Interpretacion**: Una exactitud del 90% significa que el guion es muy fiel al documento original

### 2. Sensibilidad (Recall) - **METRICA CRITICA PARA EDUCACION**
- **Que mide**: ¿El video cubrio todos los temas del examen?
- **Formula**: TP / (TP + FN)
- **Interpretacion**: Si el PDF tenia 10 definiciones y el video solo menciono 6, el Recall es 60%
- **Justificacion**: Para fines pedagogicos, buscamos un Recall alto para asegurar que el estudiante no pierda conceptos clave

### 3. Especificidad (Specificity)
- **Que mide**: ¿Que tan bueno es el sistema ignorando la "paja" (bibliografia, agradecimientos)?
- **Formula**: TN / (TN + FP)
- **Interpretacion**: Mide la capacidad de filtrar el ruido del PDF

### 4. Precision
- **Que mide**: De todo lo que dice el video, ¿cuanto es realmente cierto y util?
- **Formula**: TP / (TP + FP)
- **Interpretacion**: Si el video dice 5 datos pero 1 es una "alucinacion", la precision baja
- **Justificacion**: Una precision alta garantiza que el estudiante no aprendera datos falsos

### 5. F1-Score
- **Que mide**: Balance perfecto entre no aburrir al alumno (brevedad) y no perder informacion (completitud)
- **Formula**: 2 * (Precision * Recall) / (Precision + Recall)
- **Interpretacion**: Un F1-Score de 0.85 significa que resume bien sin perder la esencia tecnica

### 6. Tasa de Falsos Positivos (FPR)
- **Que mide**: Frecuencia de alucinaciones (informacion inventada)
- **Formula**: FP / (FP + TN)
- **Objetivo**: Cercano a 0

### 7. Tasa de Falsos Negativos (FNR)
- **Que mide**: Frecuencia de omisiones (temas importantes olvidados)
- **Formula**: FN / (FN + TP)

## Uso Basico

```python
from services.evaluacion import evaluar_guion_rapido

# Definir conceptos clave que DEBEN aparecer en el guion
conceptos_clave = [
    "redes neuronales",
    "perceptron",
    "backpropagation",
    "gradiente descendente"
]

# Definir conceptos irrelevantes que NO deben aparecer
conceptos_irrelevantes = [
    "bibliografia",
    "referencias",
    "agradecimientos"
]

# Evaluar el guion
resultado = evaluar_guion_rapido(
    guion="Texto del guion generado...",
    texto_pdf="Texto original del PDF...",
    conceptos_clave=conceptos_clave,
    conceptos_irrelevantes=conceptos_irrelevantes
)

# Ver el reporte
print(resultado['reporte'])

# Acceder a metricas individuales
metricas = resultado['metricas']
print(f"Precision: {metricas['precision']:.2%}")
print(f"Recall: {metricas['sensibilidad']:.2%}")
print(f"F1-Score: {metricas['f1_score']:.2%}")
```

## Uso Avanzado

```python
from services.evaluacion import EvaluadorGuion

# Crear evaluador personalizado
evaluador = EvaluadorGuion(
    conceptos_clave=["concepto1", "concepto2"],
    conceptos_irrelevantes=["ruido1", "ruido2"]
)

# Calcular matriz de confusion
matriz = evaluador.calcular_matriz_confusion(guion, texto_pdf)

# Calcular metricas individuales
precision = evaluador.calcular_precision(matriz)
recall = evaluador.calcular_sensibilidad(matriz)
f1 = evaluador.calcular_f1_score(matriz)

# Generar reporte completo
metricas = evaluador.evaluar_guion(guion, texto_pdf)
reporte = evaluador.generar_reporte(metricas)
print(reporte)
```

## Integracion con el Pipeline Principal

Para integrar la evaluacion en el pipeline de generacion de video:

```python
# En main.py, despues de generar el guion:
from services.evaluacion import evaluar_guion_rapido

# ... codigo existente para generar guion ...

# Evaluar el guion (opcional, solo si se proporcionan conceptos clave)
if conceptos_clave_proporcionados:
    resultado_evaluacion = evaluar_guion_rapido(
        script,
        pdf_text,
        conceptos_clave,
        conceptos_irrelevantes
    )
    
    # Agregar metricas a la respuesta
    result["metricas_evaluacion"] = resultado_evaluacion['metricas']
```

## Matriz de Confusion

La matriz de confusion clasifica el contenido del guion en 4 categorias:

- **TP (Verdadero Positivo)**: Concepto clave que estaba en el PDF y aparecio en el video ✅
- **FP (Falso Positivo)**: Informacion que no estaba en el PDF pero la IA la puso (alucinacion o ruido) ❌
- **FN (Falso Negativo)**: Concepto clave que estaba en el PDF pero la IA omitio ❌
- **TN (Verdadero Negativo)**: Informacion irrelevante que la IA correctamente ignoro ✅

## Limitaciones

1. **Deteccion de Alucinaciones**: La deteccion actual es basica y busca coincidencias de palabras. Una implementacion mas sofisticada usaria embeddings o modelos de similitud semantica.

2. **Conceptos Clave**: Los conceptos clave deben ser definidos manualmente por un experto. En el futuro, se podria usar NLP para extraerlos automaticamente.

3. **Variaciones de Texto**: El sistema busca coincidencias exactas o parciales. Variaciones semanticas pueden no detectarse.

## Ejemplo de Salida

```
================================================================================
                    REPORTE DE EVALUACION DEL GUION
================================================================================

MATRIZ DE CONFUSION:
  Verdadero Positivo (TP):    8  - Conceptos clave incluidos correctamente
  Falso Positivo (FP):        2  - Alucinaciones o ruido incluido
  Falso Negativo (FN):        2  - Conceptos clave omitidos
  Verdadero Negativo (TN):   48  - Ruido correctamente ignorado

METRICAS DE RENDIMIENTO:
  Exactitud (Accuracy):     93.33%  - Que tan limpio y completo es el guion
  Sensibilidad (Recall):    80.00%  - Que tan completo es (CRITICO para educacion)
  Especificidad:            96.00%  - Capacidad de filtrar ruido
  Precision:                80.00%  - Que tan cierto es el contenido
  F1-Score:                 80.00%  - Balance entre completitud y brevedad

TASAS DE ERROR:
  Tasa Falsos Positivos:     4.00%  - Frecuencia de alucinaciones
  Tasa Falsos Negativos:    20.00%  - Frecuencia de omisiones
```

## Notas Importantes

- Las metricas ROC y AUC no se implementaron porque requieren clasificacion binaria con probabilidades, lo cual no aplica directamente a generacion de texto.
- Para usar estas metricas en produccion, necesitas definir los conceptos clave relevantes para cada PDF.
- El sistema actual es una implementacion basica; se puede mejorar con tecnicas mas avanzadas de NLP.

