"""
Ejemplo de uso del notebook con selector unificado de evaluadores
Este código reemplaza las celdas de configuración e inicialización
"""

import os
import pandas as pd
from dotenv import load_dotenv
from evaluator_factory import create_evaluator, auto_select_evaluator
from ai_evaluator import evaluation_to_dict

# ═══════════════════════════════════════════════════════════════════════
# OPCIÓN 1: CONFIGURACIÓN CON VARIABLE DE ENTORNO (Más flexible)
# ═══════════════════════════════════════════════════════════════════════

# Cargar variables de entorno
load_dotenv()

# 🎯 SELECTOR PRINCIPAL - Cambiar esta línea para elegir evaluador
# Opciones:
#   - "gemini"  → Usa Gemini API directa (API Key)
#   - "vertex"  → Usa Vertex AI (Service Account)
EVALUATOR_TYPE = "vertex"  # 👈 CAMBIAR AQUÍ

# Crear evaluador según configuración
evaluator = create_evaluator(evaluator_type=EVALUATOR_TYPE)


# ═══════════════════════════════════════════════════════════════════════
# OPCIÓN 2: AUTODETECCIÓN (Más automático)
# ═══════════════════════════════════════════════════════════════════════

# Descomenta esta línea para usar autodetección:
# evaluator = auto_select_evaluator()


# ═══════════════════════════════════════════════════════════════════════
# OPCIÓN 3: CONFIGURACIÓN EXPLÍCITA (Más control)
# ═══════════════════════════════════════════════════════════════════════

# Para Gemini API directa:
# evaluator = create_evaluator(
#     evaluator_type="gemini",
#     gemini_api_key=os.getenv('GEMINI_API_KEY')
# )

# Para Vertex AI:
# evaluator = create_evaluator(
#     evaluator_type="vertex",
#     gcp_project_id=os.getenv('GCP_PROJECT_ID'),
#     gcp_location=os.getenv('GCP_LOCATION', 'us-central1'),
#     service_account_key_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# )


# ═══════════════════════════════════════════════════════════════════════
# EL RESTO DEL CÓDIGO ES IDÉNTICO (NO CAMBIA)
# ═══════════════════════════════════════════════════════════════════════

print("\n✅ Evaluador inicializado correctamente!")
print("Ahora puedes ejecutar las celdas de evaluación normalmente.\n")

# Ejemplo de uso (idéntico para ambos evaluadores):
"""
# Load data
test_df = pd.read_csv('Conecta/langfuse3.csv')
conversations_df = extract_conversations(test_df)

# Evaluate
results = []
for idx, row in conversations_df.head(10).iterrows():
    print(f"Evaluando {idx+1}/10: {row['trace_id']}")

    evaluation = evaluator.evaluate(
        user_question=row['user_question'],
        sources=row['sources'],
        ai_response=row['ai_response'],
        trace_id=row['trace_id'],
        session_id=row['session_id']
    )

    results.append(evaluation_to_dict(evaluation))

# Analyze
results_df = pd.DataFrame(results)
print(results_df[['trace_id', 'overall_score', 'recommendation']].head())
"""


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE VARIABLES DE ENTORNO (.env file)
# ═══════════════════════════════════════════════════════════════════════

"""
Crea un archivo .env en el directorio del proyecto con este contenido:

# ─────────────────────────────────────────────────────────────────────
# OPCIÓN A: Usar Gemini API Directa
# ─────────────────────────────────────────────────────────────────────
EVALUATOR_TYPE=gemini
GEMINI_API_KEY=your-gemini-api-key-here

# ─────────────────────────────────────────────────────────────────────
# OPCIÓN B: Usar Vertex AI
# ─────────────────────────────────────────────────────────────────────
EVALUATOR_TYPE=vertex
GCP_PROJECT_ID=gemini-evaluator-project
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/home/ghost2077/gcp-keys/gemini-evaluator-key.json

# ─────────────────────────────────────────────────────────────────────
# NOTA: Si no configuras EVALUATOR_TYPE, el sistema autodetecta
# basándose en qué credenciales estén disponibles
# ─────────────────────────────────────────────────────────────────────
"""


# ═══════════════════════════════════════════════════════════════════════
# COMPARACIÓN DE CARACTERÍSTICAS
# ═══════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────┬───────────────────────┬───────────────────────┐
│ Característica          │ Gemini API            │ Vertex AI             │
├─────────────────────────┼───────────────────────┼───────────────────────┤
│ Autenticación           │ API Key               │ Service Account       │
│ Setup                   │ Más simple            │ Requiere GCP config   │
│ Cuotas (free)           │ 1,500 RPD             │ N/A                   │
│ Cuotas (paid)           │ 2,000 RPM             │ Mucho más altas       │
│ Seguridad               │ Básica                │ Enterprise (IAM)      │
│ Monitoreo               │ No                    │ Cloud Monitoring      │
│ Logging                 │ No                    │ Cloud Logging         │
│ Costos                  │ Similar               │ Similar               │
│ Uso recomendado         │ Desarrollo/Prototipo  │ Producción/Empresa    │
└─────────────────────────┴───────────────────────┴───────────────────────┘

💡 RECOMENDACIÓN:
   - Desarrollo local:  Gemini API (más simple)
   - Producción:        Vertex AI (más robusto)
   - CI/CD en GCP:      Vertex AI con ADC
"""


# ═══════════════════════════════════════════════════════════════════════
# GUÍA DE MIGRACIÓN (Gemini API → Vertex AI)
# ═══════════════════════════════════════════════════════════════════════

"""
PASO 1: Configurar Vertex AI (una sola vez)
   Ver VERTEX_AI_SETUP.md para instrucciones detalladas

PASO 2: Actualizar .env
   # Antes:
   EVALUATOR_TYPE=gemini
   GEMINI_API_KEY=...

   # Después:
   EVALUATOR_TYPE=vertex
   GCP_PROJECT_ID=your-project
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

PASO 3: Reiniciar notebook
   No se requieren otros cambios de código ✅

PASO 4: Verificar funcionamiento
   python test_vertex_evaluator.py
"""
