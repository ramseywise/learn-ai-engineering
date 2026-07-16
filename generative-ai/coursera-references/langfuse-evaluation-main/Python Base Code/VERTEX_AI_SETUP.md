# Configuración de Vertex AI para el Evaluador

Guía completa para usar el evaluador con Vertex AI y Service Accounts en lugar de la API directa de Gemini.

## 🎯 Beneficios de Usar Vertex AI

| Característica | Gemini API Directa | Vertex AI |
|----------------|-------------------|-----------|
| **Cuotas** | 1,500 RPD (free), 2,000 RPM (paid) | Mucho más altas |
| **Autenticación** | API Key expuesta | Service Account (IAM) |
| **Control de Acceso** | API Key única | Roles IAM granulares |
| **Monitoreo** | Básico | Cloud Monitoring completo |
| **Logging** | No | Cloud Logging integrado |
| **Seguridad** | API Key en código | Credenciales rotables |
| **Enterprise** | No | Sí |

## 📋 Paso 1: Configuración en Google Cloud

### 1.1 Crear Proyecto GCP (si no tienes)

```bash
# Crear proyecto
gcloud projects create gemini-evaluator-project --name="Gemini Evaluator"

# Configurar proyecto activo
gcloud config set project gemini-evaluator-project
```

### 1.2 Habilitar APIs Necesarias

```bash
# Habilitar Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Habilitar Cloud Resource Manager (para IAM)
gcloud services enable cloudresourcemanager.googleapis.com

# Verificar APIs habilitadas
gcloud services list --enabled
```

### 1.3 Crear Service Account

```bash
# Crear service account
gcloud iam service-accounts create gemini-evaluator \
    --display-name="Gemini Evaluator Service Account" \
    --description="Service account for AI response evaluation with Gemini"

# Verificar creación
gcloud iam service-accounts list
```

### 1.4 Asignar Permisos

```bash
# Obtener email de service account
SA_EMAIL=$(gcloud iam service-accounts list \
    --filter="displayName:Gemini Evaluator" \
    --format="value(email)")

# Dar rol de usuario de Vertex AI
gcloud projects add-iam-policy-binding gemini-evaluator-project \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

# Opcional: Dar rol de viewer para monitoreo
gcloud projects add-iam-policy-binding gemini-evaluator-project \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/viewer"

# Verificar permisos
gcloud projects get-iam-policy gemini-evaluator-project \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA_EMAIL}"
```

### 1.5 Crear y Descargar Clave de Service Account

```bash
# Crear directorio para keys (fuera del repo)
mkdir -p ~/gcp-keys

# Crear y descargar key
gcloud iam service-accounts keys create ~/gcp-keys/gemini-evaluator-key.json \
    --iam-account=${SA_EMAIL}

# IMPORTANTE: Proteger el archivo
chmod 600 ~/gcp-keys/gemini-evaluator-key.json

# Verificar contenido (debe ser JSON)
cat ~/gcp-keys/gemini-evaluator-key.json | jq .type
# Output esperado: "service_account"
```

⚠️ **SEGURIDAD CRÍTICA:**
- **NUNCA** commitees este archivo a Git
- **NUNCA** lo compartas públicamente
- Guárdalo en un lugar seguro (mejor: usa Secret Manager)

### 1.6 Agregar al .gitignore

```bash
# Agregar a .gitignore
echo "*.json" >> .gitignore
echo "gcp-keys/" >> .gitignore
echo "service-account*.json" >> .gitignore
```

## 📦 Paso 2: Instalación de Dependencias

```bash
# Instalar SDK de Vertex AI
pip install google-cloud-aiplatform

# Verificar instalación
python -c "import vertexai; print('Vertex AI SDK installed successfully')"
```

## 🔧 Paso 3: Configurar Variables de Entorno

### Opción A: Usando archivo .env

```bash
# Crear archivo .env (NO COMMITEAR)
cat > .env << EOF
# Google Cloud Configuration
GCP_PROJECT_ID=gemini-evaluator-project
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/home/ghost2077/gcp-keys/gemini-evaluator-key.json
EOF

# Cargar en Python
pip install python-dotenv
```

### Opción B: Variables de entorno del sistema

```bash
# En tu .bashrc o .zshrc
export GCP_PROJECT_ID="gemini-evaluator-project"
export GCP_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/home/ghost2077/gcp-keys/gemini-evaluator-key.json"

# Recargar shell
source ~/.bashrc
```

### Opción C: Application Default Credentials (ADC)

```bash
# Para desarrollo local
gcloud auth application-default login

# Para producción en GCP (Compute Engine, Cloud Run, etc.)
# ADC se configura automáticamente, no necesitas key file
```

## ✅ Estado de Implementación

**COMPLETADO** - El evaluador Vertex AI está 100% funcional con todas las características:

- ✅ Autenticación con Service Account y ADC
- ✅ Evaluación de calidad de preguntas (Question Quality)
- ✅ Evaluación principal de respuestas (5 criterios)
- ✅ Verificación crítica para casos problemáticos
- ✅ Detección de alucinaciones
- ✅ Contexto de Davivienda integrado
- ✅ Verificación de disponibilidad de respuestas en fuentes
- ✅ Compatibilidad total con código existente

**Archivos listos para usar:**
- `ai_evaluator_vertex.py` - Implementación completa
- `test_vertex_evaluator.py` - Script de prueba
- `VERTEX_AI_SETUP.md` - Guía de configuración

## 💻 Paso 4: Uso en el Notebook

### 4.1 Modificar Cell de Configuración

```python
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración para Vertex AI
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'gemini-evaluator-project')
GCP_LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
SERVICE_ACCOUNT_KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

print(f"✅ GCP Project: {GCP_PROJECT_ID}")
print(f"✅ Location: {GCP_LOCATION}")
print(f"✅ Service Account Key: {SERVICE_ACCOUNT_KEY_PATH}")
```

### 4.2 Inicializar Evaluador

```python
from ai_evaluator_vertex import VertexGeminiEvaluator, evaluation_to_dict

# Opción 1: Con service account key file
evaluator = VertexGeminiEvaluator(
    project_id=GCP_PROJECT_ID,
    location=GCP_LOCATION,
    service_account_key_path=SERVICE_ACCOUNT_KEY_PATH
)

# Opción 2: Con Application Default Credentials (en GCP)
# evaluator = VertexGeminiEvaluator(
#     project_id=GCP_PROJECT_ID,
#     location=GCP_LOCATION
# )

print("✅ Vertex AI Evaluator initialized")
```

### 4.3 Usar Normalmente

```python
# El resto del código es idéntico
for idx, row in test_df.iterrows():
    evaluation = evaluator.evaluate(
        user_question=row['user_question'],
        sources=row['sources'],
        ai_response=row['ai_response'],
        trace_id=row['trace_id'],
        session_id=row['session_id']
    )
    results.append(evaluation_to_dict(evaluation))
```

## 🔍 Paso 5: Verificar Funcionamiento

### 5.1 Test Automático (Recomendado)

```bash
# Ejecutar script de prueba
python test_vertex_evaluator.py
```

Este script:
- ✅ Verifica conexión con Vertex AI
- ✅ Inicializa el evaluador
- ✅ Ejecuta evaluación de prueba
- ✅ Muestra resultados detallados
- ✅ Valida conversión a dict

**Output esperado:**
```
============================================================
VERTEX AI GEMINI EVALUATOR - TEST
============================================================

1. Initializing Vertex AI Evaluator...
✅ Vertex AI initialized with service account: /path/to/key.json
✅ Model initialized: gemini-2.0-flash
✅ Evaluator initialized successfully!

2. Running test evaluation...
✅ Evaluation completed successfully!

============================================================
EVALUATION RESULTS
============================================================

📝 Question Quality:
   Clarity Score: 4/5
   Needs Clarification: False

🔍 Hallucination Check:
   Detected: False
   Severity: none

⚖️  Quality Scores:
   Fidelity: 5/5
   Completeness: 5/5
   Relevance: 5/5
   Coherence: 5/5

📊 Overall Assessment:
   Overall Score: 5.00/5.0
   Quality Tier: excellent
   Recommendation: approve
   Acceptable: True

✅ All tests passed! Vertex AI evaluator is ready to use.
```

### 5.2 Test Manual en Python

```python
# Test rápido
test_result = evaluator.evaluate(
    user_question="¿Qué es una cuenta de ahorros?",
    sources="Una cuenta de ahorros es un producto bancario que permite guardar dinero.",
    ai_response="Una cuenta de ahorros es un producto que permite guardar dinero y ganar intereses.",
    trace_id="test-001",
    session_id="test-session"
)

print(f"✅ Test successful! Score: {test_result.overall_quality.overall_score}")
```

### 5.2 Verificar en Cloud Console

1. Ve a: https://console.cloud.google.com/vertex-ai
2. Navega a: **Vertex AI > Model Garden > Gemini**
3. Deberías ver tus requests en el monitoreo

## 📊 Paso 6: Monitoreo y Costos

### 6.1 Ver Uso en Cloud Console

```bash
# Ver métricas de uso
gcloud ai models describe gemini-2.0-flash \
    --region=us-central1

# Ver logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" \
    --limit=10 \
    --format=json
```

### 6.2 Configurar Alertas de Costo

1. Cloud Console > Billing > Budgets & alerts
2. Crear presupuesto
3. Configurar alertas (ej: >$10/mes)

### 6.3 Estimación de Costos

**Vertex AI Gemini 2.0 Flash:**
- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens

**Para 150 conversaciones:**
- ~450K tokens input = $0.034
- ~150K tokens output = $0.045
- **Total: ~$0.08 USD**

**Para 1,000 conversaciones:**
- ~3M tokens input = $0.23
- ~1M tokens output = $0.30
- **Total: ~$0.53 USD**

## 🔐 Paso 7: Mejores Prácticas de Seguridad

### 7.1 Usar Secret Manager (Recomendado para Producción)

```bash
# Crear secret
gcloud secrets create gemini-sa-key \
    --data-file=~/gcp-keys/gemini-evaluator-key.json \
    --replication-policy="automatic"

# Dar acceso a service account
gcloud secrets add-iam-policy-binding gemini-sa-key \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
```

```python
# En código Python
from google.cloud import secretmanager

def get_credentials_from_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Usar
key_json = get_credentials_from_secret(GCP_PROJECT_ID, "gemini-sa-key")
```

### 7.2 Rotar Claves Regularmente

```bash
# Cada 90 días, crear nueva key
gcloud iam service-accounts keys create ~/gcp-keys/gemini-evaluator-key-new.json \
    --iam-account=${SA_EMAIL}

# Después de verificar que funciona, eliminar la vieja
gcloud iam service-accounts keys list --iam-account=${SA_EMAIL}
gcloud iam service-accounts keys delete OLD_KEY_ID \
    --iam-account=${SA_EMAIL}
```

### 7.3 Principio de Menor Privilegio

```bash
# Solo dar permisos necesarios
# En lugar de roles/owner, usa roles/aiplatform.user
```

## 🚀 Paso 8: Deployment en Producción

### Para Cloud Run / Cloud Functions:

```yaml
# No necesitas service account key file
# Usa la service account del servicio
runtime: python311
env_variables:
  GCP_PROJECT_ID: "gemini-evaluator-project"
  GCP_LOCATION: "us-central1"
```

### Para Compute Engine / GKE:

```bash
# Asociar service account a la VM/pod
gcloud compute instances set-service-account INSTANCE_NAME \
    --service-account=${SA_EMAIL} \
    --scopes=https://www.googleapis.com/auth/cloud-platform
```

## 📝 Troubleshooting

### Error: "Permission denied"

```bash
# Verificar permisos
gcloud projects get-iam-policy gemini-evaluator-project \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA_EMAIL}"

# Re-asignar rol
gcloud projects add-iam-policy-binding gemini-evaluator-project \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"
```

### Error: "API not enabled"

```bash
# Habilitar Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Esperar 1-2 minutos para propagación
```

### Error: "Quota exceeded"

```bash
# Ver cuotas
gcloud compute project-info describe --project=gemini-evaluator-project

# Solicitar aumento de cuota en Cloud Console
```

## 📚 Referencias

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Service Accounts Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Gemini API Pricing](https://cloud.google.com/vertex-ai/pricing)
- [IAM Roles Reference](https://cloud.google.com/iam/docs/understanding-roles)
