# 🔄 Sistema Dual de Evaluadores - Guía Completa

## 📋 Resumen

Ahora el sistema de evaluación soporta **dos backends intercambiables**:

1. 🔵 **Gemini API Directa** - Simple, ideal para desarrollo
2. ☁️ **Vertex AI** - Enterprise, ideal para producción

**Lo mejor:** Puedes cambiar entre ellos con **un solo parámetro** sin modificar el resto del código.

---

## 🎯 ¿Por Qué Dos Opciones?

### Gemini API Directa
✅ **Ventajas:**
- Setup en 2 minutos (solo API key)
- Perfecto para desarrollo local
- Ideal para prototipos y pruebas
- No requiere cuenta GCP

⚠️ **Limitaciones:**
- Cuotas limitadas (1,500 RPD free, 2,000 RPM paid)
- Sin monitoreo integrado
- Seguridad básica (API key)
- Sin auditoría enterprise

### Vertex AI
✅ **Ventajas:**
- Cuotas empresariales (mucho más altas)
- Seguridad IAM completa
- Cloud Logging integrado
- Cloud Monitoring automático
- Auditoría completa
- Rotación de credenciales
- Control de acceso granular

⚠️ **Limitaciones:**
- Requiere proyecto GCP
- Setup inicial más complejo (10-15 min)
- Requiere service account

---

## 🚀 Inicio Rápido

### Opción A: Gemini API (Desarrollo)

```bash
# 1. Obtener API Key
# Visita: https://makersuite.google.com/app/apikey

# 2. Configurar
export GEMINI_API_KEY="your-api-key"
export EVALUATOR_TYPE="gemini"

# 3. Listo!
python -c "from evaluator_factory import create_evaluator; evaluator = create_evaluator()"
```

### Opción B: Vertex AI (Producción)

```bash
# 1. Seguir guía completa
# Ver: VERTEX_AI_SETUP.md

# 2. Configurar
export EVALUATOR_TYPE="vertex"
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# 3. Probar
python test_vertex_evaluator.py

# 4. Listo!
```

---

## 💻 Uso en Código

### Método 1: Variable de Entorno (Recomendado)

```python
from evaluator_factory import create_evaluator
from ai_evaluator import evaluation_to_dict

# Crear evaluador (lee EVALUATOR_TYPE del ambiente)
evaluator = create_evaluator()

# Usar normalmente
evaluation = evaluator.evaluate(
    user_question="...",
    sources="...",
    ai_response="...",
    trace_id="...",
    session_id="..."
)

result = evaluation_to_dict(evaluation)
```

**Para cambiar de modo:**
```bash
# Antes (Gemini API)
export EVALUATOR_TYPE="gemini"

# Después (Vertex AI)
export EVALUATOR_TYPE="vertex"

# No se requieren otros cambios de código!
```

### Método 2: Parámetro Explícito

```python
from evaluator_factory import create_evaluator

# Gemini API
evaluator = create_evaluator(
    evaluator_type="gemini",
    gemini_api_key="your-key"
)

# O Vertex AI
evaluator = create_evaluator(
    evaluator_type="vertex",
    gcp_project_id="your-project",
    service_account_key_path="/path/to/key.json"
)
```

### Método 3: Autodetección

```python
from evaluator_factory import auto_select_evaluator

# Detecta automáticamente según credenciales disponibles
# Prioridad: EVALUATOR_TYPE > GCP_PROJECT_ID > GEMINI_API_KEY
evaluator = auto_select_evaluator()
```

---

## 📁 Archivos Creados

### Nuevos Archivos

1. **`evaluator_factory.py`** ⭐ Principal
   - Factory pattern para crear evaluadores
   - Función `create_evaluator()`
   - Función `auto_select_evaluator()`
   - Configuración centralizada

2. **`ai_evaluator_vertex.py`**
   - Implementación completa de Vertex AI
   - Misma interfaz que `ai_evaluator.py`
   - Todas las características implementadas

3. **`test_both_evaluators.py`**
   - Script de comparación
   - Prueba ambos evaluadores con mismo caso
   - Muestra diferencias si las hay

4. **`test_vertex_evaluator.py`**
   - Test específico de Vertex AI
   - Verifica configuración
   - Diagnóstico de errores

5. **`notebook_example_unified.py`**
   - Ejemplo de uso en notebook
   - Muestra todas las opciones de configuración

6. **`VERTEX_AI_SETUP.md`**
   - Guía completa de configuración GCP
   - Paso a paso detallado
   - Troubleshooting

7. **`DUAL_EVALUATOR_SETUP.md`** (este archivo)
   - Guía unificada del sistema dual

8. **`IMPLEMENTATION_COMPLETE.md`**
   - Documentación de implementación
   - Checklist de validación

### Archivos Existentes (No Modificados)

- `ai_evaluator.py` - Funciona igual que antes
- `run_ai_evaluation.ipynb` - Compatible con ambos evaluadores
- `README_EVALUATION.md` - Actualizado con info del selector

---

## 🔧 Configuración

### Archivo `.env` (Recomendado)

Crea un archivo `.env` en tu proyecto:

```bash
# ─────────────────────────────────────────────────────────────────────
# OPCIÓN A: Usar Gemini API
# ─────────────────────────────────────────────────────────────────────
EVALUATOR_TYPE=gemini
GEMINI_API_KEY=AIzaSy...your-key-here

# ─────────────────────────────────────────────────────────────────────
# OPCIÓN B: Usar Vertex AI
# ─────────────────────────────────────────────────────────────────────
EVALUATOR_TYPE=vertex
GCP_PROJECT_ID=gemini-evaluator-project
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/home/user/gcp-keys/key.json

# ─────────────────────────────────────────────────────────────────────
# NOTA: Puedes tener ambas configuraciones y cambiar solo EVALUATOR_TYPE
# ─────────────────────────────────────────────────────────────────────
```

### En tu Notebook

```python
import os
from dotenv import load_dotenv
from evaluator_factory import create_evaluator

# Cargar .env
load_dotenv()

# Crear evaluador
evaluator = create_evaluator()

# El resto del código NO cambia
# ...
```

---

## 🧪 Testing

### Probar Gemini API

```bash
export GEMINI_API_KEY="your-key"
python -c "
from evaluator_factory import create_evaluator
evaluator = create_evaluator(evaluator_type='gemini', gemini_api_key='$GEMINI_API_KEY')
print('✅ Gemini API funciona!')
"
```

### Probar Vertex AI

```bash
export GCP_PROJECT_ID="your-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
python test_vertex_evaluator.py
```

### Comparar Ambos

```bash
# Configurar ambos
export GEMINI_API_KEY="your-key"
export GCP_PROJECT_ID="your-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Ejecutar comparación
python test_both_evaluators.py
```

**Output esperado:**
```
🔬 COMPARACIÓN DE EVALUADORES: GEMINI API vs VERTEX AI
============================================================

📝 Question Quality:
   Clarity Score: 4/5

🔍 Hallucination Check:
   Detected: False

📊 Overall Assessment:
   Overall Score: 5.00/5.0

✅ Resultados prácticamente idénticos
```

---

## 📊 Comparación Detallada

| Aspecto | Gemini API | Vertex AI |
|---------|------------|-----------|
| **Setup Time** | 2 minutos | 10-15 minutos |
| **Complejidad** | Muy baja | Media |
| **Requisitos** | API Key | Proyecto GCP + Service Account |
| **Cuotas Free** | 1,500 RPD | N/A |
| **Cuotas Paid** | 2,000 RPM | Mucho más altas |
| **Autenticación** | API Key | Service Account + IAM |
| **Logging** | ❌ No | ✅ Cloud Logging |
| **Monitoring** | ❌ No | ✅ Cloud Monitoring |
| **Auditoría** | ❌ No | ✅ Cloud Audit Logs |
| **Rate Limits** | Estrictos | Flexibles |
| **Rotación Credenciales** | Manual | Automática |
| **Control Acceso** | Todo o nada | Granular (IAM) |
| **Costo por 1K evals** | ~$0.56 | ~$0.56 |
| **Seguridad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Escalabilidad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Recomendado para** | Desarrollo | Producción |

---

## 🔄 Migración

### De Gemini API a Vertex AI

**Paso 1: Configurar Vertex AI (una sola vez)**
```bash
# Seguir guía completa
cat VERTEX_AI_SETUP.md
```

**Paso 2: Actualizar credenciales**
```bash
# Antes
export EVALUATOR_TYPE="gemini"
export GEMINI_API_KEY="..."

# Después
export EVALUATOR_TYPE="vertex"
export GCP_PROJECT_ID="..."
export GOOGLE_APPLICATION_CREDENTIALS="..."
```

**Paso 3: Listo!**
```bash
# No se requieren cambios de código
# Solo reiniciar kernel del notebook
```

### De Vertex AI a Gemini API

```bash
# Cambiar una línea
export EVALUATOR_TYPE="gemini"  # era "vertex"

# Todo lo demás funciona igual
```

---

## 💡 Casos de Uso Recomendados

### Usa Gemini API cuando:

✅ Estás en fase de desarrollo/prototipo
✅ Necesitas setup rápido
✅ Evaluando <1,500 conversaciones/día
✅ No tienes cuenta GCP
✅ Seguridad básica es suficiente
✅ No necesitas auditoría

### Usa Vertex AI cuando:

✅ Estás en producción
✅ Evaluando >2,000 conversaciones/día
✅ Necesitas auditoría completa
✅ Requieres seguridad enterprise
✅ Necesitas logging centralizado
✅ Tienes infraestructura en GCP
✅ Necesitas control de acceso IAM
✅ Requieres rotación de credenciales

---

## 🎯 Casos de Uso Mixtos

### Desarrollo Local + Producción en GCP

```python
# config.py
import os

def get_evaluator():
    """Usa Gemini localmente, Vertex en GCP"""
    if os.getenv('ENV') == 'production':
        return create_evaluator(evaluator_type='vertex')
    else:
        return create_evaluator(evaluator_type='gemini')
```

### CI/CD con Ambos

```yaml
# .github/workflows/test.yml
name: Tests

jobs:
  test-gemini:
    runs-on: ubuntu-latest
    env:
      EVALUATOR_TYPE: gemini
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    steps:
      - run: pytest tests/

  test-vertex:
    runs-on: ubuntu-latest
    env:
      EVALUATOR_TYPE: vertex
      GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
    steps:
      - run: pytest tests/
```

---

## 🐛 Troubleshooting

### Error: "EVALUATOR_TYPE debe ser 'gemini' o 'vertex'"

```bash
# Verificar variable
echo $EVALUATOR_TYPE

# Configurar correctamente
export EVALUATOR_TYPE="gemini"  # o "vertex"
```

### Error: "Para usar Gemini API necesitas GEMINI_API_KEY"

```bash
# Verificar API key
echo $GEMINI_API_KEY

# Configurar
export GEMINI_API_KEY="your-key"
```

### Error: "Para usar Vertex AI necesitas GCP_PROJECT_ID"

```bash
# Verificar proyecto
echo $GCP_PROJECT_ID

# Configurar
export GCP_PROJECT_ID="your-project"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Los resultados son diferentes entre evaluadores

```bash
# Esto es NORMAL
# Ambos usan el mismo modelo (gemini-2.0-flash)
# Diferencias menores (<0.5 puntos) son esperadas
# Ejecutar test comparativo:
python test_both_evaluators.py
```

---

## 📚 Referencias

- **Gemini API Docs:** https://ai.google.dev/docs
- **Vertex AI Docs:** https://cloud.google.com/vertex-ai/docs
- **Guía Vertex AI:** [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)
- **README Principal:** [README_EVALUATION.md](README_EVALUATION.md)

---

## ✅ Checklist de Validación

Antes de usar en producción:

**Para Gemini API:**
- [ ] API Key obtenida de Google AI Studio
- [ ] Variable `GEMINI_API_KEY` configurada
- [ ] Variable `EVALUATOR_TYPE="gemini"` configurada
- [ ] Test exitoso con `create_evaluator()`

**Para Vertex AI:**
- [ ] Proyecto GCP creado
- [ ] Vertex AI API habilitada
- [ ] Service Account creado
- [ ] Permisos IAM asignados
- [ ] Service Account key descargada
- [ ] Variables de entorno configuradas
- [ ] Test exitoso con `test_vertex_evaluator.py`

**Para ambos:**
- [ ] Archivo `.env` configurado
- [ ] `evaluator_factory.py` funciona
- [ ] Notebook actualizado
- [ ] Tests passing
- [ ] Documentación revisada

---

## 🎉 Conclusión

Ahora tienes un **sistema flexible** que te permite:

✅ Desarrollar localmente con Gemini API
✅ Desplegar en producción con Vertex AI
✅ Cambiar entre modos sin modificar código
✅ Probar y comparar ambos evaluadores
✅ Migrar fácilmente cuando necesites

**Cambio total requerido: 1 línea de código** 🚀

```python
# Antes
evaluator = GeminiEvaluator(api_key=GEMINI_API_KEY)

# Ahora
evaluator = create_evaluator()  # Lee EVALUATOR_TYPE del ambiente
```

---

**Fecha:** 2025-10-05
**Versión:** 1.0.0
**Estado:** Production Ready ✅
