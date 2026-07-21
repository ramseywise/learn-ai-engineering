# A/B Testing: Prompt V1 (Lenient) vs V2 (Strict)

## Executive Summary

Implementamos A/B testing para comparar dos versiones del prompt de detección de alucinaciones:

- **V1 (Lenient)**: Enfoque original con criterios subjetivos
- **V2 (Strict)**: Enfoque estricto con árbol de decisión binario y penalidades severas

**Objetivo:** Detectar con mayor precisión cuando Conecta inventa información o da información errónea.

---

## Diferencias Clave

### 1. **Filosofía**

| Aspecto | V1 (Lenient) | V2 (Strict) |
|---------|--------------|-------------|
| Tolerancia | "When in doubt, flag it" (ambiguo) | "ZERO TOLERANCE - false positives acceptable, false negatives NOT" |
| Enfoque | Subjetivo, basado en interpretación | Objetivo, árbol de decisión binario |
| Sector | Genérico | Específico bancario (compliance crítico) |

### 2. **Proceso de Evaluación**

**V1 (Lenient):**
```
1. Extract claims
2. Search for support in docs
3. Flag if "not clearly supported" ← Subjetivo
4. Assign severity based on "harm" ← Subjetivo
```

**V2 (Strict):**
```
STEP 1: EXACT MATCH
→ Quote or paraphrase exists?
   YES → Grounded ✅
   NO → Go to STEP 2

STEP 2: ENTITY CHECK
→ Same entity (product/service)?
   Doc="Fondos", Claim="Fondos" → Same, go to STEP 3
   Doc="Fondos", Claim="Fiducia" → Different, HALLUCINATION ❌

STEP 3: INFERENCE VALIDITY
→ Can be safely inferred from same entity?
   Combining Doc1+Doc2 about Product A → Valid ✅
   Applying Product A info to Product B → Invalid ❌
```

### 3. **Severity Assignment**

**V1 (Lenient):**
```
CRITICAL: "could harm customer" ← ¿Qué es harm?
MAJOR: "misleads but won't cause immediate harm" ← ¿Cuándo es immediate?
MINOR: "small details incorrect" ← ¿Qué es small?
```

**V2 (Strict) - Reglas Objetivas:**
```
CRITICAL (severity=3) - MAXIMUM PENALTY:
├─ Amounts (interest rates, fees, minimums)
├─ Contact info (phone, email, branches)
├─ Legal/compliance procedures
├─ Deadlines, timeframes
└─ Account numbers, IDs, codes

MAJOR (severity=2):
├─ Product features misrepresented
├─ Process steps incorrect
└─ Requirements fabricated

MINOR (severity=1):
├─ Product name variations (semantic same)
├─ Formatting differences
└─ Non-critical details
```

### 4. **Casos Específicos**

#### Ejemplo 1: "Fiducia Estructurada"

**Pregunta:** "como cancelo una fiducia estructurada?"
**Conecta:** "Para cancelar una fiducia estructurada, llama al 018000..."
**Documents:** Solo mencionan "Fondos de Inversión" y "Dafuturo"

**V1 (Lenient) - Comportamiento actual:**
```json
{
  "hallucination_detected": false,  ❌ INCONSISTENTE
  "severity": "none",
  "evidence": [{"status": "grounded"}],  ← Todo marcado como grounded
  "assessment": "mixing hallucination detected"  ← Pero aquí sí lo detecta
}
```

**V2 (Strict) - Comportamiento esperado:**
```json
{
  "hallucination_detected": true,  ✅ CONSISTENTE
  "severity": "critical",  ← Contact info = CRITICAL
  "hallucination_type": "entity_substitution",
  "evidence": [{
    "claim": "Para cancelar fiducia estructurada, llama al 018000...",
    "status": "hallucination",  ← Marcado correctamente
    "step_failed": 2,  ← Falló en ENTITY CHECK
    "severity": 3,
    "document_support": "NOT FOUND: Documents only cover 'Fondos' and 'Dafuturo', NOT 'fiducia estructurada'"
  }]
}
```

#### Ejemplo 2: Inferencia Válida

**Pregunta:** "Qué requisitos tiene y cuánto cuesta el producto X?"
**Documents:** Doc1 = "Producto X requiere cédula", Doc2 = "Producto X cuesta $100"
**Conecta:** "Producto X requiere cédula y cuesta $100"

**V1:** Podría marcar como "mixing" (combinando docs)
**V2:** GROUNDED ✅ (STEP 3 - Valid inference, same entity)

#### Ejemplo 3: Sustitución Inválida

**Pregunta:** "Qué requisitos tiene el producto Y?"
**Documents:** Solo "Producto X requiere cédula"
**Conecta:** "Producto Y requiere cédula"

**V1:** Podría marcar como "grounded" (requisito está en docs)
**V2:** HALLUCINATION ❌ (STEP 2 - Entity substitution)

---

## Impacto Esperado

### Tasa de Detección

**V1 (Lenient):**
- Detecta: 15-25% de conversaciones
- Principalmente: Fabricaciones obvias
- Pierde: Entity substitution, mixing sutil

**V2 (Strict):**
- Detecta: 30-50% de conversaciones (↑ 20-30%)
- Detecta: Todo lo de V1 + entity substitution + mixing
- Severidad: Más casos CRITICAL (contact info, amounts)

### Consistencia Estructural

**V1:**
- Inconsistencias entre `assessment` y `evidence` array
- Requiere validación post-procesamiento

**V2:**
- Reglas explícitas de consistencia:
  - `hallucinated_count > 0` → `detected = true`
  - `assessment` debe coincidir con `evidence`
- Campo `step_failed` indica dónde falló

### Casos Críticos

**V1:** Contact info errónea = MAJOR o MINOR (inconsistente)
**V2:** Contact info errónea = CRITICAL (siempre)

---

## Riesgos y Mitigaciones

### Riesgo 1: Falsos Positivos

**Riesgo:** V2 es tan estricto que marca casos legítimos

**Mitigación:**
- A/B test en 50+ conversaciones
- Manual review de casos "V2 only"
- Target: <10% false positive rate

**Criterio de aceptación:**
```python
false_positive_rate = cases_v2_only_invalid / cases_v2_only_total
if false_positive_rate < 0.10:
    # V2 is acceptable
elif false_positive_rate < 0.20:
    # Tune V2 (adjust entity matching rules)
else:
    # Keep V1, V2 too strict
```

### Riesgo 2: Sobrecarga de Casos

**Riesgo:** 2x más hallucinations detectadas → más trabajo de revisión

**Mitigación:**
- Priorizar por severity: CRITICAL > MAJOR > MINOR
- Automatizar correcciones para patterns comunes
- Dashboard para tracking

### Riesgo 3: Performance

**Riesgo:** Prompt V2 es más largo → más tokens → más costo/latencia

**Mitigación:**
- V2 prompt: ~2K tokens (vs V1: ~800 tokens)
- Cost increase: ~$1.20/1K conversations (de $3.70 a $4.90)
- Aceptable para mejora en detección

---

## Cómo Ejecutar el A/B Test

### Paso 1: Ejecutar Test

```bash
# Default: 20 conversations
python ab_test_prompts.py

# Custom sample size
python ab_test_prompts.py --limit 50

# Custom output
python ab_test_prompts.py --limit 100 --output-dir ./results
```

### Paso 2: Analizar Resultados

El script imprime automáticamente:
```
A/B TEST SUMMARY
================

Conversations tested: 50

📊 V1 (LENIENT PROMPT):
   Success rate: 100.0%
   Hallucination rate: 25.0% (12/50)
   Severity breakdown:
      minor: 8
      major: 3
      critical: 1

📊 V2 (STRICT PROMPT):
   Success rate: 100.0%
   Hallucination rate: 38.0% (19/50)
   Severity breakdown:
      minor: 9
      major: 5
      critical: 5

🔍 COMPARISON:
   Hallucination rate difference: +13.0%
   → V2 is moderately stricter (+13.0%)
```

### Paso 3: Manual Review

```python
# Load results
df_v1 = pd.read_csv('ab_test_results/ab_test_v1_lenient_TIMESTAMP.csv')
df_v2 = pd.read_csv('ab_test_results/ab_test_v2_strict_TIMESTAMP.csv')

# Cases where V2 detected but V1 didn't
merged = df_v1.merge(df_v2, on='session_id', suffixes=('_v1', '_v2'))
v2_only = merged[
    (merged['hall_hallucination_detected_v1'] == False) &
    (merged['hall_hallucination_detected_v2'] == True)
]

print(f"Cases to manually review: {len(v2_only)}")

# Review critical cases first
critical_v2_only = v2_only[v2_only['hall_severity_v2'] == 'critical']
print(f"\nCritical cases (review first): {len(critical_v2_only)}")
```

### Paso 4: Decidir

**Usar V2 (Strict) si:**
- False positive rate < 10%
- Detecta ≥80% de critical cases de V1
- Detecta 20-50% más hallucinations totales

**Mantener V1 (Lenient) si:**
- False positive rate > 20%
- V2 pierde critical cases de V1
- V2 detecta >80% más (demasiado estricto)

**Ajustar V2 si:**
- False positive rate 10-20%
- Demasiados MINOR escalados a MAJOR

---

## Implementación de Cambios

### Usar V2 por Default

Edita `src/config.py`:

```python
@dataclass
class EvaluatorConfig:
    # ...
    # A/B Testing
    prompt_version: str = "v2"  # Changed from "v1"
```

### Uso Selectivo

```python
# V1 para análisis exploratorio
config_v1 = EvaluatorConfig(prompt_version="v1")
orchestrator_v1 = EvaluationOrchestrator(config_v1)

# V2 para detección crítica
config_v2 = EvaluatorConfig(prompt_version="v2")
orchestrator_v2 = EvaluationOrchestrator(config_v2)
```

---

## Ejemplo de Output Comparado

### Caso: "Fiducia Estructurada"

#### V1 Output (Inconsistente):
```
🚨 HALLUCINATION CHECK:
   Detected: False  ← WRONG
   Severity: none
   Grounding Ratio: 100.00%  ← WRONG
   Assessment: "mixing hallucination detected"  ← RIGHT (but ignored)
```

#### V2 Output (Consistente):
```
🚨 HALLUCINATION CHECK:
   Detected: True  ← CORRECT
   Severity: critical  ← CORRECT (contact info)
   Grounding Ratio: 0.00%  ← CORRECT
   Step Failed: 2 (Entity Check)
   Assessment: "Entity substitution - applying info from 'Fondos' to 'Fiducia' without evidence"
```

---

## Recursos

- **Script de testing:** `ab_test_prompts.py`
- **Guía de análisis:** `notebooks/ab_test_analysis.md`
- **Código fuente V1:** `src/utils/prompt_templates.py::_hallucination_detector_v1()`
- **Código fuente V2:** `src/utils/prompt_templates.py::_hallucination_detector_v2()`

---

## Métricas de Éxito

### Objetivo Principal
Reducir hallucinations de 25% → <15% en 6 meses

### Métricas A/B Test
- V2 detecta ≥90% de critical cases de V1
- V2 detecta 20-40% más total hallucinations
- False positive rate <10%
- Consistencia estructural: 100% (no más assessment vs evidence mismatch)

### Métricas Post-Implementación
- Critical hallucinations detectadas: 100% (vs ~60% actual)
- Tiempo de revisión manual: -30% (mejor clasificación por severity)
- Compliance risk: Reducido (contact info errors = CRITICAL)
