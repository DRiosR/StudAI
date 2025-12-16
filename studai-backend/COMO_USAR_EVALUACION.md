# Como Usar el Modulo de Evaluacion

Esta guia te explica como ejecutar y usar el modulo de evaluacion de metricas.

## Opcion 1: Script Interactivo (MAS FACIL)

### Paso 1: Ejecutar el script
```bash
cd studai-backend
python evaluar_guion.py
```

### Paso 2: Seguir las instrucciones
El script te pedira:
1. Ruta al PDF (o presiona Enter para usar ejemplo)
2. Conceptos clave que deben aparecer en el guion
3. Conceptos irrelevantes que no deben aparecer (opcional)

### Paso 3: Ver resultados
El script mostrara un reporte completo con todas las metricas.

---

## Opcion 2: Ejecutar Ejemplo Rapido

Si solo quieres ver como funciona sin un PDF:

```bash
cd studai-backend
python evaluar_guion.py
# Presiona Enter cuando pida la ruta del PDF
```

Esto ejecutara un ejemplo predefinido.

---

## Opcion 3: Usar desde Codigo Python

### Ejemplo Basico

```python
from services.evaluacion import evaluar_guion_rapido

# Definir conceptos clave
conceptos_clave = [
    "redes neuronales",
    "perceptron",
    "backpropagation"
]

# Definir conceptos irrelevantes
conceptos_irrelevantes = [
    "bibliografia",
    "referencias"
]

# Evaluar
resultado = evaluar_guion_rapido(
    guion="Texto del guion generado...",
    texto_pdf="Texto original del PDF...",
    conceptos_clave=conceptos_clave,
    conceptos_irrelevantes=conceptos_irrelevantes
)

# Ver reporte
print(resultado['reporte'])

# Acceder a metricas individuales
metricas = resultado['metricas']
print(f"Precision: {metricas['precision']:.2%}")
print(f"Recall: {metricas['sensibilidad']:.2%}")
```

---

## Opcion 4: Ejecutar Ejemplo Completo

```bash
cd studai-backend
python services/ejemplo_evaluacion.py
```

Esto ejecutara el ejemplo personalizado que viene en el archivo.

---

## Ejemplo de Uso Completo con PDF

```bash
# 1. Asegurate de tener un PDF en la carpeta photos/
cd studai-backend

# 2. Ejecuta el evaluador
python evaluar_guion.py photos/tu_archivo.pdf

# 3. Ingresa los conceptos clave cuando te los pida
# Ejemplo: redes neuronales, perceptron, backpropagation, gradiente descendente

# 4. Ingresa conceptos irrelevantes (opcional)
# Ejemplo: bibliografia, referencias, agradecimientos

# 5. Ver el reporte de evaluacion
```

---

## Que Hace el Evaluador?

1. **Extrae texto del PDF** (si usas el script completo)
2. **Genera un guion** usando la IA (si usas el script completo)
3. **Busca conceptos clave** en el guion generado
4. **Detecta alucinaciones** (informacion inventada)
5. **Calcula todas las metricas**:
   - Exactitud (Accuracy)
   - Sensibilidad (Recall) - CRITICO para educacion
   - Especificidad
   - Precision
   - F1-Score
   - Tasa de Falsos Positivos
   - Tasa de Falsos Negativos
6. **Genera un reporte** con interpretacion

---

## Interpretacion de Resultados

### Exactitud (Accuracy)
- **> 90%**: Excelente - El guion es muy fiel al documento
- **70-90%**: Bueno - El guion es moderadamente fiel
- **< 70%**: Necesita mejora

### Sensibilidad (Recall) - MAS IMPORTANTE
- **> 80%**: Excelente - Cubre casi todos los conceptos clave
- **60-80%**: Bueno - Cubre la mayoria de conceptos
- **< 60%**: Necesita mejora - Faltan muchos conceptos importantes

### Precision
- **> 80%**: Excelente - Casi todo el contenido es veraz
- **60-80%**: Bueno - La mayoria del contenido es veraz
- **< 60%**: Necesita mejora - Hay muchas alucinaciones

### F1-Score
- **> 0.8**: Excelente balance entre completitud y brevedad
- **0.6-0.8**: Bueno balance
- **< 0.6**: Necesita mejora

---

## Preguntas Frecuentes

### ¿Donde debo poner los conceptos clave?
Los conceptos clave los defines TU basandote en el contenido del PDF. Son los temas importantes que quieres que aparezcan en el video.

### ¿Como se detectan las alucinaciones?
El sistema busca oraciones en el guion que no tienen palabras similares en el PDF original. Es una deteccion basica pero efectiva.

### ¿Puedo usar esto en produccion?
Si, pero necesitas definir los conceptos clave para cada PDF. En el futuro se podria automatizar esto con NLP.

### ¿Que pasa si no tengo conceptos clave?
El sistema usara una lista por defecto, pero los resultados seran menos precisos. Es mejor definir conceptos especificos para cada PDF.

---

## Solucion de Problemas

### Error: "No module named 'services'"
```bash
# Asegurate de estar en el directorio correcto
cd studai-backend
python evaluar_guion.py
```

### Error: "File not found"
Verifica que la ruta al PDF sea correcta y que el archivo exista.

### Error: "Azure OpenAI key not set"
Asegurate de tener configuradas las variables de entorno en tu archivo `.env`.

---

## Integracion en el Pipeline

Si quieres evaluar automaticamente cada guion generado, puedes modificar `main.py`:

```python
# Despues de generar el guion en main.py
from services.evaluacion import evaluar_guion_rapido

# Si tienes conceptos clave definidos
if conceptos_clave:
    resultado = evaluar_guion_rapido(
        script,
        pdf_text,
        conceptos_clave,
        conceptos_irrelevantes
    )
    # Agregar metricas a la respuesta
    result["metricas_evaluacion"] = resultado['metricas']
```

