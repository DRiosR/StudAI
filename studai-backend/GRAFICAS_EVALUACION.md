# Graficas de Evaluacion

El modulo de evaluacion ahora genera graficas visuales para mejor comprension de las metricas.

## 📊 Graficas Generadas

### 1. Matriz de Confusion (Heatmap)
**Archivo:** `matriz_confusion.png`

**Que muestra:**
- Visualizacion de la matriz de confusion en formato heatmap
- Colores: Verde (valores altos) a Rojo (valores bajos)
- Muestra TP, FP, FN, TN de forma visual

**Como interpretarla:**
- Mas verde en TP y TN = Mejor rendimiento
- Mas rojo en FP y FN = Necesita mejora

### 2. Metricas Principales (Barras)
**Archivo:** `metricas_principales.png`

**Que muestra:**
- Grafica de barras con las 5 metricas principales
- Colores:
  - 🟢 Verde: Metrica > 70% (Excelente)
  - 🟡 Amarillo: Metrica 50-70% (Bueno)
  - 🔴 Rojo: Metrica < 50% (Necesita mejora)
- Lineas de referencia en 70% y 50%

**Metricas mostradas:**
- Exactitud (Accuracy)
- Sensibilidad (Recall)
- Especificidad
- Precision
- F1-Score

### 3. Comparacion de Metricas (Radar Chart)
**Archivo:** `radar_metricas.png`

**Que muestra:**
- Grafica tipo radar (spider chart) comparando todas las metricas
- Permite ver rapidamente cuales metricas estan mejor/peor
- Area mas grande = mejor rendimiento general

**Como interpretarla:**
- Forma mas circular y grande = Mejor rendimiento balanceado
- Forma irregular = Algunas metricas mejores que otras

### 4. Distribucion de Conceptos (Pie Charts)
**Archivo:** `distribucion_conceptos.png`

**Que muestra:**
- Dos graficas de pastel:
  1. Conceptos clave: Incluidos (TP) vs Omitidos (FN)
  2. Conceptos irrelevantes: Ignorados (TN) vs Incluidos (FP)

**Como interpretarla:**
- Mas verde = Mejor (conceptos clave incluidos, ruido ignorado)
- Mas rojo = Necesita mejora (conceptos omitidos, ruido incluido)

## 🚀 Como Usar

### Opcion 1: Automatico (Recomendado)
Las graficas se generan automaticamente al ejecutar:
```bash
python evaluar_guion.py
```

Las graficas se guardan en: `output/graficas/`

### Opcion 2: Desde Codigo
```python
from services.evaluacion import evaluar_guion_rapido

resultado = evaluar_guion_rapido(
    guion="...",
    texto_pdf="...",
    conceptos_clave=["...", "..."],
    generar_graficas=True,  # Activar graficas
    output_dir_graficas="output/graficas"  # Donde guardar
)

# Acceder a las rutas de las graficas
if 'graficas' in resultado:
    for nombre, ruta in resultado['graficas'].items():
        print(f"{nombre}: {ruta}")
```

### Opcion 3: Solo Generar Graficas
```python
from services.evaluacion import EvaluadorGuion

evaluador = EvaluadorGuion(conceptos_clave, conceptos_irrelevantes)
metricas = evaluador.evaluar_guion(guion, texto_pdf)

# Generar solo las graficas
rutas = evaluador.generar_graficas(metricas, "output/graficas")
```

## 📦 Requisitos

Para usar las graficas, necesitas instalar:
```bash
pip install matplotlib numpy
```

Si no estan instalados, el sistema funcionara igual pero sin graficas (solo mostrara el reporte de texto).

## 📁 Archivos Generados

Cuando ejecutas la evaluacion, se crean estos archivos en `output/graficas/`:

1. `matriz_confusion.png` - Matriz de confusion visual
2. `metricas_principales.png` - Grafica de barras de metricas
3. `radar_metricas.png` - Grafica radar comparativa
4. `distribucion_conceptos.png` - Graficas de pastel de distribucion

## 💡 Ejemplo de Uso Completo

```python
from services.evaluacion import evaluar_guion_rapido

# Evaluar y generar graficas
resultado = evaluar_guion_rapido(
    guion="Texto del guion...",
    texto_pdf="Texto del PDF...",
    conceptos_clave=["IA", "redes neuronales", "aprendizaje"],
    conceptos_irrelevantes=["bibliografia", "referencias"],
    generar_graficas=True
)

# Ver reporte
print(resultado['reporte'])

# Ver rutas de graficas
if 'graficas' in resultado:
    print("\nGraficas generadas:")
    for nombre, ruta in resultado['graficas'].items():
        print(f"  - {nombre}: {ruta}")
```

## 🎨 Personalizacion

Las graficas usan colores y estilos predefinidos, pero puedes modificar:
- Colores en `_grafica_metricas_principales()` (linea de colores)
- Tamaño de figuras en `figsize=(ancho, alto)`
- Resolucion en `dpi=150` (aumentar para mayor calidad)

## ⚠️ Notas

- Las graficas se generan en formato PNG
- Si matplotlib no esta instalado, el sistema funcionara sin graficas
- Las graficas se guardan automaticamente, no se muestran en pantalla (backend)

