"""
Evaluator Factory - Selector de evaluadores (Gemini API vs Vertex AI)
Permite cambiar entre evaluadores con un simple parámetro
"""

import os
from typing import Literal, Optional
from ai_evaluator import GeminiEvaluator
from ai_evaluator_vertex import VertexGeminiEvaluator

EvaluatorType = Literal["gemini", "vertex"]


class EvaluatorConfig:
    """
    Configuración centralizada para seleccionar evaluador

    Ejemplo de uso:

    # Opción 1: Variable de entorno
    export EVALUATOR_TYPE="vertex"  # o "gemini"

    # Opción 2: Parámetro directo
    evaluator = create_evaluator(evaluator_type="vertex")
    """

    # Tipo de evaluador por defecto (puede sobreescribirse con env var)
    DEFAULT_EVALUATOR = "gemini"  # Cambiar a "vertex" para usar Vertex AI por defecto

    @staticmethod
    def get_evaluator_type() -> EvaluatorType:
        """Obtiene el tipo de evaluador desde env var o default"""
        evaluator_type = os.getenv('EVALUATOR_TYPE', EvaluatorConfig.DEFAULT_EVALUATOR).lower()

        if evaluator_type not in ["gemini", "vertex"]:
            raise ValueError(f"EVALUATOR_TYPE debe ser 'gemini' o 'vertex', recibido: {evaluator_type}")

        return evaluator_type


def create_evaluator(
    evaluator_type: Optional[EvaluatorType] = None,
    # Parámetros para Gemini API
    gemini_api_key: Optional[str] = None,
    # Parámetros para Vertex AI
    gcp_project_id: Optional[str] = None,
    gcp_location: str = "us-central1",
    service_account_key_path: Optional[str] = None
):
    """
    Factory function para crear el evaluador apropiado

    Args:
        evaluator_type: "gemini" o "vertex". Si None, usa EVALUATOR_TYPE env var o default
        gemini_api_key: API key para Gemini API directa (si evaluator_type="gemini")
        gcp_project_id: GCP Project ID (si evaluator_type="vertex")
        gcp_location: GCP location (default: us-central1)
        service_account_key_path: Path a service account key (si evaluator_type="vertex")

    Returns:
        GeminiEvaluator o VertexGeminiEvaluator (ambos con la misma interfaz)

    Ejemplos:

    # 1. Usar Gemini API directa
    evaluator = create_evaluator(
        evaluator_type="gemini",
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )

    # 2. Usar Vertex AI
    evaluator = create_evaluator(
        evaluator_type="vertex",
        gcp_project_id=os.getenv('GCP_PROJECT_ID'),
        service_account_key_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )

    # 3. Autodetección desde env vars
    evaluator = create_evaluator()  # Lee EVALUATOR_TYPE del ambiente
    """

    # Determinar tipo de evaluador
    if evaluator_type is None:
        evaluator_type = EvaluatorConfig.get_evaluator_type()

    print(f"\n{'='*60}")
    print(f"🤖 Inicializando evaluador: {evaluator_type.upper()}")
    print(f"{'='*60}\n")

    if evaluator_type == "gemini":
        # Usar Gemini API directa
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ValueError(
                "Para usar Gemini API necesitas:\n"
                "  1. Pasar gemini_api_key como parámetro, O\n"
                "  2. Configurar GEMINI_API_KEY en variables de entorno"
            )

        print(f"📡 Modo: Gemini API Directa")
        print(f"🔑 API Key: {api_key[:20]}...{api_key[-4:]}")
        print(f"📊 Cuotas: 1,500 RPD (free) / 2,000 RPM (paid)")

        return GeminiEvaluator(api_key=api_key)

    elif evaluator_type == "vertex":
        # Usar Vertex AI
        project_id = gcp_project_id or os.getenv('GCP_PROJECT_ID')
        location = gcp_location or os.getenv('GCP_LOCATION', 'us-central1')
        sa_key_path = service_account_key_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        if not project_id:
            raise ValueError(
                "Para usar Vertex AI necesitas:\n"
                "  1. Pasar gcp_project_id como parámetro, O\n"
                "  2. Configurar GCP_PROJECT_ID en variables de entorno"
            )

        print(f"☁️  Modo: Vertex AI (Enterprise)")
        print(f"📦 Proyecto: {project_id}")
        print(f"📍 Location: {location}")

        if sa_key_path:
            print(f"🔐 Auth: Service Account ({sa_key_path})")
        else:
            print(f"🔐 Auth: Application Default Credentials (ADC)")

        print(f"📊 Cuotas: Mucho más altas (enterprise)")
        print(f"🔒 Seguridad: IAM + Cloud Logging + Cloud Monitoring")

        return VertexGeminiEvaluator(
            project_id=project_id,
            location=location,
            service_account_key_path=sa_key_path
        )

    else:
        raise ValueError(f"evaluator_type debe ser 'gemini' o 'vertex', recibido: {evaluator_type}")


def auto_select_evaluator():
    """
    Selección automática inteligente basada en variables de entorno disponibles

    Prioridad:
    1. Si EVALUATOR_TYPE está configurado → usar ese
    2. Si GCP_PROJECT_ID está configurado → usar Vertex AI
    3. Si GEMINI_API_KEY está configurado → usar Gemini API
    4. Default → usar configuración por defecto

    Returns:
        Evaluador apropiado inicializado
    """

    # 1. EVALUATOR_TYPE explícito
    if os.getenv('EVALUATOR_TYPE'):
        return create_evaluator()

    # 2. Detectar si hay credenciales de Vertex AI
    if os.getenv('GCP_PROJECT_ID') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("🔍 Autodetección: Encontradas credenciales de Vertex AI")
        return create_evaluator(evaluator_type="vertex")

    # 3. Detectar si hay API key de Gemini
    if os.getenv('GEMINI_API_KEY'):
        print("🔍 Autodetección: Encontrada API key de Gemini")
        return create_evaluator(evaluator_type="gemini")

    # 4. Usar default
    print(f"🔍 Autodetección: Usando evaluador por defecto ({EvaluatorConfig.DEFAULT_EVALUATOR})")
    return create_evaluator()


# Ejemplos de uso
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           EVALUATOR FACTORY - SELECTOR DE EVALUADORES                ║
╚══════════════════════════════════════════════════════════════════════╝

Opciones de uso:

1️⃣  VARIABLE DE ENTORNO (Recomendado)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   # Para usar Gemini API directa:
   export EVALUATOR_TYPE="gemini"
   export GEMINI_API_KEY="your-api-key"

   # Para usar Vertex AI:
   export EVALUATOR_TYPE="vertex"
   export GCP_PROJECT_ID="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

   # En código:
   evaluator = create_evaluator()


2️⃣  PARÁMETRO EXPLÍCITO
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   # Gemini API:
   evaluator = create_evaluator(
       evaluator_type="gemini",
       gemini_api_key="your-key"
   )

   # Vertex AI:
   evaluator = create_evaluator(
       evaluator_type="vertex",
       gcp_project_id="your-project",
       service_account_key_path="/path/to/key.json"
   )


3️⃣  AUTODETECCIÓN INTELIGENTE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   # Selecciona automáticamente según env vars disponibles:
   evaluator = auto_select_evaluator()


4️⃣  CAMBIAR DEFAULT EN CÓDIGO
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   # Editar evaluator_factory.py, línea 21:
   DEFAULT_EVALUATOR = "vertex"  # o "gemini"


═══════════════════════════════════════════════════════════════════════

💡 AMBOS EVALUADORES TIENEN LA MISMA INTERFAZ:

   # El código de evaluación NO cambia:
   result = evaluator.evaluate(
       user_question="...",
       sources="...",
       ai_response="...",
       trace_id="...",
       session_id="..."
   )

   # Solo cambias CÓMO creas el evaluator
   # Todo lo demás permanece idéntico ✅

═══════════════════════════════════════════════════════════════════════
    """)
