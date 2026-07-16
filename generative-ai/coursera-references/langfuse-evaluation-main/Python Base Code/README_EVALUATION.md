# AI Response Quality Evaluation System

Sistema de evaluación automática de respuestas de AI usando Gemini 2.0 Flash con arquitectura híbrida.

**🆕 NUEVO:** Ahora soporta **dos modos de ejecución** que se pueden cambiar con un simple parámetro:
- 🔵 **Gemini API Directa** - Para desarrollo y prototipado (setup simple)
- ☁️ **Vertex AI** - Para producción enterprise (seguridad IAM, cuotas altas, monitoreo)

Ver [🔄 Selector de Evaluadores](#-selector-de-evaluadores) para cambiar entre modos.

---

## 🎯 Objetivo

Evaluar si el AI está respondiendo correctamente según los documentos consultados, detectando:
- ❌ Alucinaciones (información inventada)
- ❌ Mezcla incorrecta de información
- ❌ Respuestas incompletas
- ❌ Información irrelevante o incoherente

## 🏗️ Arquitectura: Opción D (Híbrida) con Question-Aware Evaluation

```
Input (User Question + Sources + AI Response)
    ↓
Agent 0: Question Quality Evaluator (100% casos)
    → Evalúa: claridad, ambigüedad, completitud de contexto
    ↓
Agent 1: Evaluador Principal (100% casos, question-aware)
    → Ajusta criterios según calidad de pregunta
    → IF flagged (hallucination major/critical O score < 3):
        → Agent 2: Verificador Crítico (solo ~18% casos)
    ↓
JSON estructurado final
```

**Ventajas:**
- Costo controlado: +12% vs evaluación simple (por question evaluator adicional)
- Precisión contextual: Evalúa respuestas considerando calidad de pregunta
- Velocidad: 82% de casos = 2 llamadas (question + main)
- Detección de preguntas vagas: Identifica cuándo el AI debe pedir clarificación

## 📊 Criterios Evaluados

### 0. Calidad de la Pregunta (NUEVO)
- **Clarity score (1-5)**: Qué tan específica es la pregunta
  - 1 = Extremadamente vaga (ej: "tarjeta de crédito")
  - 5 = Muy específica (ej: "requisitos tarjeta Visa Gold persona natural")
- **Context completeness (1-5)**: Tiene contexto necesario
- **Is ambiguous**: Boolean - pregunta puede interpretarse de múltiples formas
- **Question type**: informational, procedural, comparative, troubleshooting, vague
- **Needs clarification**: Boolean - AI debería pedir más información
- **Missing information**: Lista de datos faltantes
- **Clarification needed**: Lista de preguntas que el AI debería hacer

**Impacto en evaluación:**
- Si `clarity_score ≤ 2` (pregunta vaga):
  - Es ACEPTABLE que el AI pida clarificación
  - NO se penaliza `completeness` si la pregunta era ambigua
  - Se EVALÚA si las preguntas clarificadoras del AI son apropiadas
- Si `clarity_score ≥ 4` (pregunta específica):
  - La respuesta DEBE ser completa y precisa
  - NO es aceptable pedir clarificación innecesariamente

## 📊 Criterios Evaluados (Response)

### 1. Detección de Alucinaciones (CRÍTICO)
- **Tipos detectados**: URLs, emails, hechos, procedimientos, mezcla de fuentes
- **Severidad**: none, minor, major, critical
- **Output**: Evidencia exacta del texto inventado

### 2. Fidelidad a Fuentes
- **Escala 1-5**: Qué % de la respuesta está soportado por fuentes
- **Grounding ratio**: Ratio de claims soportados vs totales
- **Output**: Lista de claims no soportados

### 3. Completitud
- **Escala 1-5**: Responde todos los aspectos de la pregunta
- **Completeness rate**: % de aspectos respondidos
- **Output**: Aspectos faltantes

### 4. Relevancia
- **Escala 1-5**: Respuesta pertinente (no divaga)
- **Relevance ratio**: % de contenido relevante
- **Output**: Contenido irrelevante detectado

### 5. Coherencia Lógica
- **Escala 1-5**: Sin contradicciones internas
- **Output**: Contradicciones específicas detectadas

### 6. Evaluación Global
- **Acceptable**: true/false (decisión binaria)
- **Quality tier**: excellent, good, acceptable, poor, critical
- **Overall score**: 1.0-5.0 (promedio ponderado)
- **Recommendation**: approve, review, reject

## 💰 Costos Estimados

Para **1,000 conversaciones** con Gemini 1.5 Flash:

| Componente | Tokens | Costo |
|------------|--------|-------|
| Input (prompts) | ~3.5M | $0.26 |
| Output (JSON) | ~1.0M | $0.30 |
| **TOTAL** | - | **~$0.56** |

- Costo por conversación: **$0.00056**
- Question evaluator: +10% (~130 tokens input, ~120 tokens output por caso)
- Verificación crítica adicional: +8% (~18% de casos)
- **Total overhead vs evaluación simple: ~12%**

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install google-generativeai pandas matplotlib seaborn
```

### 2. Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una API key
3. Configúrala como variable de entorno:

```bash
export GEMINI_API_KEY='tu-api-key-aqui'
```

O directamente en el notebook (no commitear):
```python
GEMINI_API_KEY = 'tu-api-key-aqui'
```

### 3. Estructura de archivos

```
claude-projects/
├── ai_evaluator.py              # Sistema evaluación (Gemini API)
├── ai_evaluator_vertex.py       # Sistema evaluación (Vertex AI)
├── evaluator_factory.py         # 🆕 Selector unificado
├── run_ai_evaluation.ipynb      # Notebook principal
├── test_both_evaluators.py      # 🆕 Comparación de evaluadores
├── test_vertex_evaluator.py     # 🆕 Test Vertex AI
├── Conecta/
│   └── langfuse3.csv           # Dataset original
├── README_EVALUATION.md         # Este archivo
└── VERTEX_AI_SETUP.md          # 🆕 Guía Vertex AI
```

## 🔄 Selector de Evaluadores

**NUEVO:** Ahora puedes cambiar entre Gemini API y Vertex AI con un simple parámetro.

### Opción 1: Variable de Entorno (Recomendado)

```python
# En tu .env file o notebook
import os
from evaluator_factory import create_evaluator

# Configurar modo
os.environ['EVALUATOR_TYPE'] = 'gemini'  # o 'vertex'

# Crear evaluador (el resto del código NO cambia)
evaluator = create_evaluator()
```

### Opción 2: Parámetro Explícito

```python
from evaluator_factory import create_evaluator

# Gemini API
evaluator = create_evaluator(
    evaluator_type="gemini",
    gemini_api_key=os.getenv('GEMINI_API_KEY')
)

# O Vertex AI
evaluator = create_evaluator(
    evaluator_type="vertex",
    gcp_project_id=os.getenv('GCP_PROJECT_ID'),
    service_account_key_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
)
```

### Opción 3: Autodetección

```python
from evaluator_factory import auto_select_evaluator

# Detecta automáticamente según credenciales disponibles
evaluator = auto_select_evaluator()
```

### Comparación de Evaluadores

| Característica | Gemini API | Vertex AI |
|----------------|------------|-----------|
| **Setup** | ✅ Muy simple | ⚠️ Requiere GCP config |
| **Autenticación** | API Key | Service Account (IAM) |
| **Cuotas** | 1,500 RPD (free), 2,000 RPM (paid) | 🚀 Mucho más altas |
| **Seguridad** | Básica | 🔒 Enterprise (IAM, logging) |
| **Monitoreo** | ❌ No | ✅ Cloud Monitoring |
| **Costos** | Similar | Similar |
| **Uso recomendado** | Desarrollo, prototipado | 🏢 Producción, empresa |

**Migración Gemini → Vertex AI:**
1. Seguir [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)
2. Cambiar `EVALUATOR_TYPE='vertex'` en .env
3. Listo! ✅ (código idéntico)

### Probar Ambos Evaluadores

```bash
# Configurar credenciales para ambos
export GEMINI_API_KEY="your-key"
export GCP_PROJECT_ID="your-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Ejecutar comparación
python test_both_evaluators.py
```

---

## 📖 Uso

### Evaluación de Prueba (10 conversaciones)

```python
# En el notebook run_ai_evaluation.ipynb
# Ejecuta hasta la sección "4. Run Evaluation"
# Esto evalúa solo 10 conversaciones para probar

TEST_SIZE = 10
# ... código ejecuta automáticamente
```

### Evaluación Completa

```python
# Descomenta el código en la sección "5. Run FULL Evaluation"
# Esto evalúa todas las conversaciones del dataset

BATCH_SIZE = 50  # Procesa en lotes
# ... descomenta el bloque completo
```

## 📈 Output

### 1. Archivos CSV

- `evaluation_results_YYYYMMDD_HHMMSS.csv` - Resultados completos
- `critical_hallucinations_YYYYMMDD_HHMMSS.csv` - Solo casos críticos

**Columnas principales:**
```
trace_id, session_id,

# Question Quality (NUEVO)
question_clarity_score, question_context_completeness,
question_is_ambiguous, question_type,
question_needs_clarification, question_missing_information,

# Response Evaluation
hallucination_detected, hallucination_severity, hallucination_evidence,
fidelity_score, grounding_ratio,
completeness_score, completeness_rate,
relevance_score, coherence_score,
overall_score, quality_tier, recommendation,
verification_applied, question_aware_adjustment
```

### 2. Reportes JSON

- `evaluation_summary_YYYYMMDD_HHMMSS.json` - Estadísticas agregadas

```json
{
  "total_conversations": 1000,
  "mean_overall_score": 3.8,
  "acceptable_rate": 0.75,
  "hallucination_rate": 0.12,
  "critical_hallucinations": 15,
  "approval_rate": 0.70,
  "review_rate": 0.22,
  "reject_rate": 0.08,
  "verification_rate": 0.18
}
```

### 3. Visualizaciones

- `evaluation_analysis.png` - 6 gráficos de análisis

## 🔍 Análisis de Resultados

### Identificar Casos Críticos

```python
# Casos con alucinaciones graves
critical = results_df[
    (results_df['hallucination_severity'].isin(['major', 'critical']))
]

# Casos de baja calidad
low_quality = results_df[results_df['overall_score'] < 2.5]

# Casos que necesitan revisión
to_review = results_df[results_df['recommendation'] == 'review']
```

### Estadísticas por Criterio

```python
print(f"Mean Fidelity Score: {results_df['fidelity_score'].mean():.2f}")
print(f"Hallucination Rate: {results_df['hallucination_detected'].mean():.2%}")
print(f"Approval Rate: {(results_df['recommendation']=='approve').mean():.2%}")
```

### Distribución de Problemas

```python
# Tipos de alucinaciones más comunes
results_df['hallucination_types'].value_counts()

# Severidad de problemas
results_df['hallucination_severity'].value_counts()
```

### Análisis de Calidad de Preguntas (NUEVO)

```python
# Distribución de claridad de preguntas
print(f"Mean Clarity Score: {results_df['question_clarity_score'].mean():.2f}")
print(results_df['question_type'].value_counts())

# Preguntas vagas que necesitan clarificación
vague_questions = results_df[results_df['question_clarity_score'] <= 2]
print(f"Vague Questions: {len(vague_questions)} ({len(vague_questions)/len(results_df)*100:.1f}%)")

# Correlación entre claridad de pregunta y calidad de respuesta
correlation = results_df['question_clarity_score'].corr(results_df['overall_score'])
print(f"Question Clarity ↔ Overall Score: {correlation:.3f}")

# Casos donde preguntas vagas llevaron a respuestas incompletas
vague_incomplete = results_df[
    (results_df['question_clarity_score'] <= 2) &
    (results_df['completeness_score'] < 3)
]
```

### Ejemplos Detallados de Evaluación (NUEVO)

El notebook incluye funciones para inspeccionar el razonamiento completo del agente evaluador:

```python
# Ver evaluación detallada de un caso específico
display_evaluation_example(analysis_df, 0)  # Primer caso
display_evaluation_example(analysis_df, 5, show_sources=True)  # Con fuentes

# Comparar dos casos lado a lado
compare_evaluations(analysis_df, 0, 3)  # Compara caso 1 vs caso 4
```

**Qué muestra `display_evaluation_example()`:**
- 📝 Pregunta original del usuario
- 🔍 Evaluación de calidad de la pregunta (clarity, ambigüedad, missing info)
- 🤖 Respuesta del AI
- 📚 Fuentes consultadas (opcional)
- ⚖️ Evaluación completa de la respuesta:
  - Overall score y quality tier
  - Detección de alucinaciones con evidencia
  - Scores individuales (fidelity, completeness, relevance, coherence)
  - Análisis de claims (soportados vs no soportados)
  - Aspectos faltantes
  - Verificación crítica (si aplicó)
  - Ajustes por calidad de pregunta
- 💭 Razonamiento final del evaluador

**Ejemplos automáticos:**
El notebook también genera automáticamente ejemplos de:
- ✅ Mejor caso (highest score)
- ❌ Peor caso (lowest score)
- 🚨 Caso con alucinación
- ⚠️ Caso con pregunta vaga
- ✅ Caso con pregunta específica

Esto permite inspeccionar cómo el agente está razonando y validar que está evaluando correctamente.

## ⚙️ Personalización

### Ajustar criterios de verificación

En `ai_evaluator.py`, línea ~380:

```python
needs_verification = (
    result_dict['hallucination_check']['detected'] and
    result_dict['hallucination_check']['severity'] in ['major', 'critical']
) or (
    result_dict['overall_quality']['overall_score'] < 3.0
)
```

Cambia los umbrales según tus necesidades:
- `< 3.0` → `< 2.5` (menos verificaciones)
- `< 3.0` → `< 3.5` (más verificaciones)

### Ajustar ponderación de scores

En el prompt (ai_evaluator.py, línea ~220):

```python
OVERALL SCORE: promedio ponderado
- fidelity_score × 0.35    # Peso de fidelidad
- completeness × 0.25       # Peso de completitud
- relevance × 0.20          # Peso de relevancia
- coherence × 0.20          # Peso de coherencia
```

## 🐛 Troubleshooting

### Error: "API key not configured"

```bash
export GEMINI_API_KEY='your-key-here'
```

### Error: "JSON Parse Error"

El modelo a veces devuelve markdown. El parser lo maneja automáticamente, pero si falla:
1. Revisa el `response_text` en el error
2. Ajusta la temperatura en `generation_config` (línea 48)

### Error: "Rate limit exceeded"

Gemini Flash 2.0 tiene rate limits:
- **Free tier**: 15 RPM (requests per minute)
- **Paid tier**: 1000 RPM

Solución:
```python
import time
# Agregar delay entre requests
time.sleep(1)  # 1 segundo entre llamadas
```

### Costo demasiado alto

1. Evalúa muestra más pequeña primero
2. Ajusta umbral de verificación para reducir casos verificados
3. Usa batches más pequeños

## 📚 Referencias

- [Gemini API Docs](https://ai.google.dev/docs)
- [Gemini Pricing](https://ai.google.dev/pricing)
- [Python SDK](https://github.com/google/generative-ai-python)

## 🤝 Contribuciones

Para mejorar el sistema:

1. **Mejorar prompts**: Los prompts están en `ai_evaluator.py`
2. **Agregar métricas**: Modificar `EvaluationResult` dataclass
3. **Nuevos análisis**: Agregar celdas en el notebook

## 📝 Changelog

### v1.0 (2025-01-XX)
- Sistema inicial con arquitectura híbrida
- Evaluación de 5 criterios principales
- Detección de alucinaciones con verificación
- Export a CSV y JSON
- Visualizaciones automáticas
