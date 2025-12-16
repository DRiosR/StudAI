# README: Sistema de Evaluacion de Guiones Generados por IA

## 📋 Indice

1. [¿Que es este sistema?](#que-es-este-sistema)
2. [¿Como funciona?](#como-funciona)
3. [Metricas que evalua](#metricas-que-evalua)
4. [Conceptos clave del codigo](#conceptos-clave-del-codigo)
5. [Como usar el sistema](#como-usar-el-sistema)
6. [Interpretacion de resultados](#interpretacion-de-resultados)

---

## ¿Que es este sistema?

Este sistema evalua la calidad de los guiones generados automaticamente por IA a partir de PDFs academicos. Mide que tan bien el guion:

- **Incluye** los conceptos importantes del documento original
- **Excluye** informacion irrelevante (bibliografia, referencias, etc.)
- **Evita alucinaciones** (informacion inventada por la IA)
- **Mantiene fidelidad** al contenido original

---

## ¿Como funciona?

### Proceso paso a paso:

1. **Extraccion de texto del PDF**
   - Lee el PDF y extrae todo el texto
   - Si el PDF es escaneado (imagen), usa OCR (Reconocimiento Optico de Caracteres)

2. **Generacion del guion por IA**
   - El modelo de lenguaje (LLM) genera un guion corto basado en el texto del PDF
   - El guion es mas corto y adaptado para video

3. **Evaluacion del guion**
   - Compara el guion generado con el texto original del PDF
   - Identifica que conceptos clave estan presentes o ausentes
   - Detecta si hay informacion inventada (alucinaciones)
   - Calcula metricas de rendimiento

4. **Generacion de reportes y graficas**
   - Crea un reporte de texto con todas las metricas
   - Genera graficas visuales para mejor comprension

---

## Metricas que evalua

### 1. Matriz de Confusion

La base de todas las metricas. Clasifica cada concepto en 4 categorias:

- **TP (Verdadero Positivo)**: Conceptos clave que estan en el PDF Y en el guion ✅
- **FP (Falso Positivo)**: Conceptos que estan en el guion PERO NO en el PDF (alucinaciones) ❌
- **FN (Falso Negativo)**: Conceptos clave que estan en el PDF PERO NO en el guion (omisiones) ⚠️
- **TN (Verdadero Negativo)**: Conceptos irrelevantes que NO estan ni en el PDF ni en el guion ✅

**Ejemplo:**
```
PDF tiene: "redes neuronales", "perceptron", "bibliografia"
Guion tiene: "redes neuronales", "algoritmo nuevo" (inventado)

TP = 1 (redes neuronales esta en ambos)
FP = 1 (algoritmo nuevo no esta en el PDF)
FN = 1 (perceptron esta en PDF pero no en guion)
TN = 1 (bibliografia no esta en ninguno - correcto)
```

### 2. Exactitud (Accuracy)

**Formula:** `(TP + TN) / (TP + TN + FP + FN)`

**Que mide:** Que tan "limpio y completo" es el guion en general.

**Interpretacion:**
- 90%+ = Excelente: El guion es muy fiel al documento
- 70-90% = Bueno: El guion es moderadamente fiel
- <70% = Necesita mejora: Hay muchos errores u omisiones

### 3. Sensibilidad (Recall)

**Formula:** `TP / (TP + FN)`

**Que mide:** ¿El video cubrio todos los temas importantes del documento?

**CRITICO PARA EDUCACION:** Si el PDF tenia 10 conceptos clave y el video solo menciono 6, el Recall es 60%.

**Interpretacion:**
- 90%+ = Excelente: Cubrio casi todos los conceptos importantes
- 70-90% = Bueno: Cubrio la mayoria de conceptos
- <70% = Necesita mejora: Faltan muchos conceptos importantes

### 4. Especificidad (Specificity)

**Formula:** `TN / (TN + FP)`

**Que mide:** ¿Que tan bueno es el sistema ignorando la "paja" (bibliografia, agradecimientos)?

**Interpretacion:**
- 90%+ = Excelente: Filtra muy bien el ruido
- 70-90% = Bueno: Filtra la mayoria del ruido
- <70% = Necesita mejora: Incluye mucha informacion irrelevante

### 5. Precision

**Formula:** `TP / (TP + FP)`

**Que mide:** De todo lo que dice el video, ¿cuanto es realmente cierto y util?

**CRITICO:** Una precision alta garantiza que el estudiante no aprendera datos falsos.

**Interpretacion:**
- 90%+ = Excelente: Casi todo el contenido es veraz
- 70-90% = Bueno: La mayoria del contenido es veraz
- <70% = Necesita mejora: Hay muchas alucinaciones

### 6. F1-Score

**Formula:** `2 * (Precision * Recall) / (Precision + Recall)`

**Que mide:** Balance perfecto entre no aburrir al alumno (brevedad) y no perder informacion (completitud).

**Interpretacion:**
- 0.85+ = Excelente: Resume bien sin perder la esencia tecnica
- 0.70-0.85 = Bueno: Buen balance
- <0.70 = Necesita mejora: O es muy largo o falta informacion

### 7. Tasa de Falsos Positivos (FPR)

**Formula:** `FP / (FP + TN)`

**Que mide:** Con que frecuencia la IA inventa cosas (alucinaciones).

**Objetivo:** Cercano a 0%

### 8. Tasa de Falsos Negativos (FNR)

**Formula:** `FN / (FN + TP)`

**Que mide:** Con que frecuencia la IA olvida temas importantes (omisiones).

**Objetivo:** Cercano a 0%

---

## Conceptos clave del codigo

### 1. Clase `EvaluadorGuion`

**Ubicacion:** `services/evaluacion.py`

**Responsabilidad:** Contiene toda la logica de evaluacion.

**Metodos principales:**

- `calcular_matriz_confusion(guion, texto_pdf)`: Compara el guion con el PDF y clasifica conceptos
- `evaluar_guion(guion, texto_pdf)`: Evalua un guion completo y retorna todas las metricas
- `generar_reporte(metricas)`: Crea un reporte legible de texto
- `generar_graficas(metricas, output_dir)`: Genera graficas visuales

### 2. Deteccion de conceptos

**Como funciona:**

1. **Extraccion flexible de conceptos del guion:**
   - Busca conceptos clave en el guion
   - No requiere coincidencia exacta (50% de palabras importantes)
   - Ejemplo: Si buscas "redes neuronales", encuentra "redes neuronales artificiales"

2. **Deteccion de alucinaciones:**
   - Analiza cada oracion del guion
   - Verifica si al menos 20% de las palabras importantes aparecen en el PDF
   - Si no, marca como alucinacion

3. **Extraccion automatica de conceptos:**
   - Analiza el PDF y encuentra palabras frecuentes
   - Filtra palabras comunes (stop words)
   - Sugiere conceptos clave automaticamente

**Codigo importante:**

```python
def extraer_conceptos_del_guion(self, guion: str, conceptos: List[str]) -> Set[str]:
    """
    Extrae conceptos que aparecen en el guion.
    Usa matching flexible: 50% de palabras importantes deben coincidir.
    """
    # Divide el guion en oraciones
    # Para cada concepto, busca si aparece (con flexibilidad)
    # Retorna conjunto de conceptos encontrados
```

```python
def detectar_alucinaciones(self, guion: str, texto_pdf: str) -> int:
    """
    Detecta oraciones que no tienen base en el PDF.
    Si menos del 20% de palabras importantes coinciden, es alucinacion.
    """
    # Divide el guion en oraciones
    # Para cada oracion, verifica si tiene base en el PDF
    # Cuenta cuantas son alucinaciones
```

### 3. Calculo de metricas

**Todas las metricas se calculan a partir de la matriz de confusion:**

```python
matriz = {
    'TP': 8,   # Conceptos clave incluidos correctamente
    'FP': 2,   # Alucinaciones
    'FN': 3,   # Conceptos clave omitidos
    'TN': 5    # Ruido correctamente ignorado
}

# Ejemplo: Exactitud
exactitud = (TP + TN) / (TP + TN + FP + FN)
exactitud = (8 + 5) / (8 + 5 + 2 + 3) = 13/18 = 72.2%
```

### 4. Generacion de graficas

**Graficas generadas:**

1. **Matriz de Confusion (Heatmap)**
   - Visualiza TP, FP, FN, TN con colores
   - Verde = valores altos, Rojo = valores bajos

2. **Metricas Principales (Barras)**
   - Grafica de barras con las 5 metricas principales
   - Colores: Verde (>70%), Amarillo (50-70%), Rojo (<50%)

3. **Comparacion de Metricas (Radar)**
   - Grafica tipo radar comparando todas las metricas
   - Permite ver rapidamente el rendimiento general

4. **Distribucion de Conceptos (Pie Charts)**
   - Dos graficas de pastel:
     - Conceptos clave: Incluidos vs Omitidos
     - Conceptos irrelevantes: Ignorados vs Incluidos

**Tecnologia:** `matplotlib` (opcional, se maneja si no esta instalado)

### 5. Extraccion automatica de conceptos

**Funcion:** `extraer_conceptos_clave_automatico(texto_pdf, num_conceptos=10)`

**Como funciona:**

1. Convierte el texto a minusculas
2. Extrae palabras de 5+ caracteres (mas significativas)
3. Filtra palabras comunes (stop words en espanol e ingles)
4. Cuenta frecuencias de aparicion
5. Retorna las palabras mas frecuentes (que aparecen al menos 2 veces)

**Ejemplo:**
```
PDF tiene: "redes neuronales", "redes neuronales profundas", "redes convolucionales"
Resultado: ["redes", "neuronales", "convolucionales", "profundas"]
```

---

## Como usar el sistema

### Opcion 1: Script interactivo (Recomendado)

```bash
python evaluar_guion.py
```

El script te pedira:
1. Ruta del PDF
2. Ruta del guion generado (o lo genera automaticamente)
3. Conceptos clave (puedes usar sugerencias automaticas)
4. Conceptos irrelevantes (opcional)
5. Si guardar resultados

### Opcion 2: Desde codigo Python

```python
from services.evaluacion import evaluar_guion_rapido

resultado = evaluar_guion_rapido(
    guion="Texto del guion generado...",
    texto_pdf="Texto extraido del PDF...",
    conceptos_clave=["concepto1", "concepto2", "concepto3"],
    conceptos_irrelevantes=["bibliografia", "referencias"],
    generar_graficas=True
)

# Ver reporte
print(resultado['reporte'])

# Ver metricas
print(resultado['metricas'])

# Ver rutas de graficas
if 'graficas' in resultado:
    for nombre, ruta in resultado['graficas'].items():
        print(f"{nombre}: {ruta}")
```

### Opcion 3: Uso avanzado (clase EvaluadorGuion)

```python
from services.evaluacion import EvaluadorGuion

# Crear evaluador
evaluador = EvaluadorGuion(
    conceptos_clave=["IA", "redes neuronales", "aprendizaje"],
    conceptos_irrelevantes=["bibliografia", "referencias"]
)

# Evaluar guion
metricas = evaluador.evaluar_guion(guion, texto_pdf)

# Generar reporte
reporte = evaluador.generar_reporte(metricas)
print(reporte)

# Generar graficas
rutas = evaluador.generar_graficas(metricas, "output/graficas")
```

---

## Interpretacion de resultados

### Ejemplo de reporte:

```
================================================================================
                    REPORTE DE EVALUACION DEL GUION
================================================================================

MATRIZ DE CONFUSION:
  Verdadero Positivo (TP):    8  - Conceptos clave incluidos correctamente
  Falso Positivo (FP):        2  - Alucinaciones o ruido incluido
  Falso Negativo (FN):        3  - Conceptos clave omitidos
  Verdadero Negativo (TN):    5  - Ruido correctamente ignorado

METRICAS DE RENDIMIENTO:
  Exactitud (Accuracy):     72.22%  - Que tan limpio y completo es el guion
  Sensibilidad (Recall):    72.73%  - Que tan completo es (CRITICO para educacion)
  Especificidad:            71.43%  - Capacidad de filtrar ruido
  Precision:                80.00%  - Que tan cierto es el contenido
  F1-Score:                 76.19%  - Balance entre completitud y brevedad

TASAS DE ERROR:
  Tasa Falsos Positivos:    28.57%  - Frecuencia de alucinaciones
  Tasa Falsos Negativos:    27.27%  - Frecuencia de omisiones
```

### ¿Que significa esto?

- **Exactitud 72%**: El guion es moderadamente fiel al documento
- **Recall 73%**: Cubrio la mayoria de los conceptos importantes (bueno para educacion)
- **Precision 80%**: El 80% del contenido es veraz (bajo riesgo de alucinaciones)
- **F1-Score 76%**: Buen balance entre completitud y brevedad

### Recomendaciones segun resultados:

**Si el Recall es bajo (<70%):**
- El guion esta omitiendo muchos conceptos importantes
- Considera aumentar la longitud del guion
- Revisa los prompts del modelo de lenguaje

**Si la Precision es baja (<70%):**
- Hay muchas alucinaciones
- El modelo esta inventando informacion
- Considera ajustar los prompts para ser mas conservador

**Si la Especificidad es baja (<70%):**
- El guion incluye mucha informacion irrelevante
- Mejora la deteccion de conceptos irrelevantes
- Filtra mejor el contenido del PDF antes de generar el guion

**Si el F1-Score es bajo (<70%):**
- El guion no tiene buen balance
- Puede ser muy corto (falta informacion) o muy largo (incluye ruido)
- Ajusta los parametros de generacion del guion

---

## Archivos importantes

### `services/evaluacion.py`
- Contiene toda la logica de evaluacion
- Clase `EvaluadorGuion`
- Funciones de extraccion automatica de conceptos
- Funciones de generacion de graficas

### `evaluar_guion.py`
- Script interactivo para ejecutar evaluaciones
- Maneja entrada del usuario
- Guarda resultados y graficas

### `services/genScript.py`
- Genera el guion usando Azure OpenAI
- Extrae texto del PDF
- Usa OCR si es necesario

---

## Requisitos

### Librerias necesarias:

```bash
pip install matplotlib numpy
```

**Nota:** Si matplotlib no esta instalado, el sistema funcionara igual pero sin graficas.

### Variables de entorno:

No se requieren variables de entorno para la evaluacion (solo para generar guiones).

---

## Ejemplo completo de uso

```bash
# 1. Ejecutar evaluacion
python evaluar_guion.py

# 2. Ingresar ruta del PDF
Ruta del PDF: test_files/mi_documento.pdf

# 3. El sistema extrae texto y genera guion automaticamente
# 4. Sugiere conceptos clave automaticamente
# 5. Seleccionar conceptos clave (o usar sugerencias)
# 6. Ingresar conceptos irrelevantes (opcional)
# 7. Ver reporte y graficas
# 8. Guardar resultados (opcional)

# Resultado:
# - evaluacion_mi_documento.txt (reporte de texto)
# - graficas_mi_documento/ (directorio con 4 graficas PNG)
```

---

## Preguntas frecuentes

### ¿Cuantos conceptos clave debo usar?

**Recomendacion:**
- Videos cortos (1-2 min): 5-8 conceptos
- Videos medianos (2-5 min): 8-12 conceptos
- Videos largos (5+ min): 12-20 conceptos

Ver `GUIA_CONCEPTOS_IDEALES.md` para mas detalles.

### ¿Que hacer si las metricas son bajas?

1. **Revisa los conceptos clave**: Asegurate de que sean realmente importantes
2. **Ajusta los prompts**: Modifica como se genera el guion en `genScript.py`
3. **Aumenta la longitud**: Si el Recall es bajo, el guion puede ser muy corto
4. **Filtra mejor el PDF**: Si la Precision es baja, puede haber mucho ruido en el PDF

### ¿Las graficas se generan automaticamente?

Si, cuando ejecutas `evaluar_guion.py` o `evaluar_guion_rapido()` con `generar_graficas=True`.

### ¿Puedo evaluar sin conceptos clave?

No, los conceptos clave son necesarios para calcular las metricas. Pero puedes usar la extraccion automatica para sugerir conceptos.

---

## Contacto y soporte

Para preguntas o problemas, revisa:
- `README_EVALUACION.md`: Guia rapida de uso
- `COMO_USAR_EVALUACION.md`: Instrucciones paso a paso
- `GUIA_CONCEPTOS_IDEALES.md`: Recomendaciones sobre cantidad de conceptos
- `GRAFICAS_EVALUACION.md`: Documentacion sobre las graficas

