"""
AI Response Quality Evaluator - Vertex AI Version
Uses Gemini via Vertex AI with Service Account authentication
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dataclasses import dataclass, asdict
import pandas as pd
from datetime import datetime

# Import all dataclasses from original evaluator
from ai_evaluator import (
    HallucinationCheck,
    FidelityScore,
    Completeness,
    Relevance,
    Coherence,
    QuestionQuality,
    OverallQuality,
    EvaluationResult
)


class VertexGeminiEvaluator:
    """
    Main evaluator using Gemini via Vertex AI with Service Account

    Benefits over direct API:
    - Higher quotas
    - Better IAM control
    - No exposed API keys
    - Enterprise-grade security
    - Better monitoring
    """

    def __init__(self,
                 project_id: str,
                 location: str = "us-central1",
                 service_account_key_path: Optional[str] = None):
        """
        Initialize Vertex AI Gemini Evaluator

        Args:
            project_id: Google Cloud Project ID
            location: GCP region (default: us-central1)
            service_account_key_path: Path to service account JSON key file
                                     If None, uses Application Default Credentials (ADC)
        """
        self.project_id = project_id
        self.location = location

        # Initialize Vertex AI
        if service_account_key_path:
            # Use service account key file
            credentials = service_account.Credentials.from_service_account_file(
                service_account_key_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            vertexai.init(
                project=project_id,
                location=location,
                credentials=credentials
            )
            print(f"✅ Vertex AI initialized with service account: {service_account_key_path}")
        else:
            # Use Application Default Credentials
            vertexai.init(project=project_id, location=location)
            print(f"✅ Vertex AI initialized with ADC for project: {project_id}")

        # Initialize Gemini model
        self.model = GenerativeModel('gemini-2.0-flash')

        # Generation config
        self.generation_config = GenerationConfig(
            temperature=0.1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )

        print(f"✅ Model initialized: gemini-2.0-flash")
        print(f"   Project: {project_id}")
        print(f"   Location: {location}")

    def _build_question_evaluation_prompt(self, user_question: str) -> str:
        """Build prompt to evaluate user question quality"""
        return f"""Eres un experto en análisis de preguntas de usuarios en contexto bancario.

⚠️  CONTEXTO CRÍTICO DEL SISTEMA:
═══════════════════════════════════════════════════════════
Este sistema es usado por FUNCIONARIOS del BANCO DAVIVIENDA para consultar:
- Información sobre procesos internos del banco
- Productos y servicios de Davivienda
- Políticas y procedimientos del banco

REGLAS DE INTERPRETACIÓN:
1. Cuando el usuario dice "el banco" → se refiere a DAVIVIENDA
2. Los usuarios son funcionarios que conocen terminología bancaria
3. Las preguntas son en contexto de trabajo interno
4. NO marques como ambiguo si el contexto es claro para un funcionario
═══════════════════════════════════════════════════════════

TU TAREA: Evaluar la CALIDAD de la pregunta del usuario para determinar si es suficientemente clara y específica, CONSIDERANDO el contexto de funcionarios de Davivienda.

PREGUNTA DEL USUARIO:
{user_question}

═══════════════════════════════════════════════════════════
CRITERIOS DE EVALUACIÓN
═══════════════════════════════════════════════════════════

1. CLARIDAD/ESPECIFICIDAD (clarity_score: 1-5)
   1 = Extremadamente vaga (ej: "tarjeta")
   2 = Muy vaga (ej: "información sobre tarjeta de crédito")
   3 = Moderadamente clara (ej: "requisitos tarjeta de crédito")
   4 = Clara (ej: "requisitos tarjeta Visa Gold para persona natural")
   5 = Muy específica (ej: "requisitos tarjeta Visa Gold persona natural ingresos >3M")

2. COMPLETITUD DE CONTEXTO (context_completeness: 1-5)
   ¿La pregunta incluye contexto necesario? (tipo cliente, producto específico, acción deseada)

3. AMBIGÜEDAD (is_ambiguous: boolean)
   ¿La pregunta puede interpretarse de múltiples formas diferentes?
   Ej: "tarjeta" → ¿solicitar? ¿consultar saldo? ¿bloquear? ¿activar?

4. POSIBLES INTERPRETACIONES (possible_interpretations: list)
   Si es ambigua, lista las posibles interpretaciones

5. TIPO DE PREGUNTA (question_type)
   - "informational": busca información (ej: "¿qué es...?")
   - "procedural": busca pasos/proceso (ej: "¿cómo...?")
   - "comparative": compara opciones (ej: "¿cuál es mejor...?")
   - "troubleshooting": problema a resolver (ej: "no puedo...")
   - "vague": demasiado vaga para clasificar

6. INFORMACIÓN FALTANTE (missing_information: list)
   ¿Qué información adicional sería útil para responder mejor?

7. NECESITA CLARIFICACIÓN (needs_clarification: boolean)
   true SI: clarity_score <= 2 O is_ambiguous = true O context_completeness <= 2

8. CLARIFICACIONES NECESARIAS (clarification_needed: list)
   ¿Qué preguntas específicas debería hacer el AI para clarificar?

═══════════════════════════════════════════════════════════
OUTPUT ESPERADO (JSON)
═══════════════════════════════════════════════════════════

{{
  "clarity_score": 1-5,
  "context_completeness": 1-5,
  "is_ambiguous": boolean,
  "possible_interpretations": ["interpretación 1", "interpretación 2"],
  "question_type": "informational" | "procedural" | "comparative" | "troubleshooting" | "vague",
  "missing_information": ["aspecto faltante 1", "aspecto faltante 2"],
  "needs_clarification": boolean,
  "clarification_needed": ["pregunta clarificadora 1", "pregunta clarificadora 2"],
  "explanation": "Explicación breve de por qué esta pregunta tiene esta calidad"
}}

NO agregues texto antes o después del JSON.
NO uses markdown.
Solo JSON puro.
"""

    def _build_main_prompt(self, user_question: str, sources: str, ai_response: str,
                          question_quality: Dict) -> str:
        """Build the detailed evaluation prompt (now question-aware)"""
        return f"""Eres un evaluador experto de respuestas de AI en contexto bancario.

⚠️  CONTEXTO CRÍTICO DEL SISTEMA:
═══════════════════════════════════════════════════════════
Este AI asiste a FUNCIONARIOS del BANCO DAVIVIENDA para consultar:
- Información sobre procesos internos del banco
- Productos y servicios de Davivienda
- Políticas y procedimientos del banco

REGLAS DE INTERPRETACIÓN:
1. Cuando el usuario dice "el banco" → se refiere a DAVIVIENDA
2. Los usuarios son funcionarios que conocen terminología bancaria
3. Las fuentes provienen de documentos internos de Davivienda
4. El AI debe responder en contexto de un funcionario consultando info interna
═══════════════════════════════════════════════════════════

DATOS DE EVALUACIÓN:
- Pregunta usuario: {user_question}
- Fuentes disponibles: {sources}
- Respuesta del AI: {ai_response}

CALIDAD DE LA PREGUNTA DEL USUARIO:
{json.dumps(question_quality, indent=2, ensure_ascii=False)}

TU TAREA: Evaluar la respuesta según criterios ESTRICTOS, CONSIDERANDO:
1. El contexto de funcionarios de Davivienda
2. La calidad de la pregunta del usuario

═══════════════════════════════════════════════════════════
⚠️  IMPORTANTE: AJUSTE SEGÚN CALIDAD DE PREGUNTA
═══════════════════════════════════════════════════════════

Si clarity_score <= 2 (pregunta vaga):
- Es ACEPTABLE que el AI pida clarificación
- NO penalices completeness si la pregunta era ambigua
- EVALÚA si el AI identificó correctamente la ambigüedad
- EVALÚA si las preguntas clarificadoras del AI son apropiadas

Si clarity_score >= 4 (pregunta específica):
- La respuesta DEBE ser completa y precisa
- NO es aceptable pedir clarificación innecesariamente
- Evalúa normalmente con criterios estrictos

═══════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════
CRITERIO 1: DETECCIÓN DE ALUCINACIONES (CRÍTICO)
═══════════════════════════════════════════════════════════

DEFINICIÓN: Alucinación = cualquier información en la respuesta que NO esté explícitamente en las fuentes.

TIPOS de alucinación:
1. URLS/emails inventados (ej: "visita www.banco.com" si no está en fuentes)
2. Datos factuales falsos (números, fechas, nombres que no aparecen)
3. Procedimientos inventados (pasos no mencionados en fuentes)
4. Mezcla incorrecta (combinar info de Doc A y Doc B de forma incoherente)

SEVERIDAD:
- "none": 0 alucinaciones detectadas
- "minor": Detalles triviales agregados (ej: emojis, conectores naturales)
- "major": Información sustantiva no soportada (ej: requisito no mencionado)
- "critical": Información falsa peligrosa (ej: URL falsa, dato legal incorrecto)

INSTRUCCIONES:
1. Lee TODAS las fuentes palabra por palabra
2. Lee la respuesta del AI palabra por palabra
3. Por CADA afirmación en la respuesta, pregúntate: "¿esto está textualmente en las fuentes?"
4. Si NO está → marca como alucinación
5. Extrae el texto EXACTO inventado
6. Clasifica el tipo y severidad

OUTPUT esperado:
{{{{
  "hallucination_check": {{{{
    "detected": boolean,
    "severity": "none" | "minor" | "major" | "critical",
    "evidence": ["texto exacto inventado 1", "texto exacto 2"],
    "type": ["url", "email", "fact", "procedure", "mixed_sources"],
    "explanation": "Por qué consideras esto alucinación"
  }}}}
}}}}

═══════════════════════════════════════════════════════════
CRITERIO 2: FIDELIDAD A FUENTES
═══════════════════════════════════════════════════════════

Evalúa qué % de la respuesta está directamente soportado por las fuentes.

ESCALA 1-5:
1 = Ungrounded: <20% soportado, mayoría inventado
2 = Partially grounded: 20-50% soportado, muchas suposiciones
3 = Mostly grounded: 50-80% soportado, algunos saltos lógicos
4 = Fully grounded: 80-95% soportado, inferencias razonables
5 = Perfect grounding: 100% soportado, citas directas/paráfrasis fieles

INSTRUCCIONES:
1. Identifica cada claim/afirmación en la respuesta
2. Para cada una, busca evidencia en fuentes
3. Marca claims sin soporte
4. Calcula ratio: claims_soportados / claims_totales

OUTPUT:
{{{{
  "fidelity_score": {{{{
    "score": 1-5,
    "grounding_level": "fully_grounded" | "mostly_grounded" | "partially_grounded" | "ungrounded",
    "total_claims": int,
    "supported_claims": int,
    "unsupported_claims": ["claim sin evidencia 1", "claim 2"],
    "grounding_ratio": float (0.0-1.0)
  }}}}
}}}}

═══════════════════════════════════════════════════════════
CRITERIO 3: COMPLETITUD
═══════════════════════════════════════════════════════════

Evalúa si la respuesta responde TODOS los aspectos de la pregunta.

⚠️  REGLA CRÍTICA: VERIFICAR SI LAS FUENTES CONTENÍAN LA RESPUESTA
═══════════════════════════════════════════════════════════
ANTES de evaluar completeness, verifica:
1. ¿Las FUENTES contienen la respuesta directa a la pregunta del usuario?
2. Si SÍ contienen la respuesta:
   - El AI DEBE proporcionarla directamente
   - Pedir clarificación innecesaria = score MUY BAJO (1-2)
   - Marca "unnecessary_clarification": true
3. Si NO contienen la respuesta:
   - Es ACEPTABLE que el AI pida clarificación
   - Marca "sources_had_answer": false

EJEMPLO:
Pregunta: "cuales son los montos de inembargabilidad"
Fuentes: "Judicial: $52,385,727; Coactivo: $35,587,500"
Respuesta AI: "¿Se refiere a judicial o coactivo?"
→ sources_had_answer: TRUE
→ unnecessary_clarification: TRUE
→ score: 1 (INCOMPLETO - info estaba disponible pero no la proporcionó)

═══════════════════════════════════════════════════════════

ESCALA 1-5:
1 = No responde: Ignora completamente la pregunta O pide clarificación innecesaria cuando fuentes tienen la respuesta
2 = Muy incompleto: Responde <30% de aspectos preguntados
3 = Parcialmente completo: Responde 30-70% de aspectos
4 = Mayormente completo: Responde 70-90%, omite detalles menores
5 = Completo: Responde 100% de lo preguntado + contexto útil

INSTRUCCIONES:
1. PRIMERO: Verifica si fuentes contienen respuesta directa
2. Descompón la pregunta en aspectos específicos
   Ej: "¿Cómo abrir cuenta y qué documentos?" → 2 aspectos
3. Verifica si la respuesta aborda cada aspecto
4. Identifica aspectos faltantes
5. Calcula completeness_rate

OUTPUT:
{{{{
  "completeness": {{{{
    "score": 1-5,
    "question_aspects": ["aspecto 1", "aspecto 2"],
    "answered_aspects": ["aspecto 1"],
    "missing_aspects": ["aspecto 2"],
    "completeness_rate": float (0.0-1.0),
    "sources_had_answer": boolean,
    "unnecessary_clarification": boolean
  }}}}
}}}}

═══════════════════════════════════════════════════════════
CRITERIO 4: RELEVANCIA
═══════════════════════════════════════════════════════════

Evalúa si la respuesta es pertinente a la pregunta (no divaga).

ESCALA 1-5:
1 = Irrelevante: Respuesta sobre tema diferente
2 = Mayormente irrelevante: <30% relacionado con pregunta
3 = Parcialmente relevante: 30-70% on-topic, algo de ruido
4 = Mayormente relevante: 70-95% on-topic, divagaciones menores
5 = Totalmente relevante: 100% enfocado, 0 información innecesaria

INSTRUCCIONES:
1. Identifica el tema central de la pregunta
2. Analiza si la respuesta se mantiene en tema
3. Detecta tangentes o información no solicitada
4. Calcula % de contenido relevante

OUTPUT:
{{{{
  "relevance": {{{{
    "score": 1-5,
    "is_on_topic": boolean,
    "main_topic": "tema identificado",
    "irrelevant_content": "texto no pertinente",
    "relevance_ratio": float (0.0-1.0)
  }}}}
}}}}

═══════════════════════════════════════════════════════════
CRITERIO 5: COHERENCIA LÓGICA
═══════════════════════════════════════════════════════════

Evalúa consistencia interna (sin contradicciones).

ESCALA 1-5:
1 = Incoherente: Contradicciones graves, ilógico
2 = Mayormente incoherente: Múltiples contradicciones
3 = Parcialmente coherente: 1-2 contradicciones menores
4 = Coherente: Sin contradicciones, flujo lógico
5 = Perfectamente coherente: Argumentación impecable

INSTRUCCIONES:
1. Busca afirmaciones que se contradigan entre sí
2. Verifica que conclusiones sigan de premisas
3. Detecta saltos lógicos injustificados
4. Identifica contradicciones específicas

OUTPUT:
{{{{
  "coherence": {{{{
    "score": 1-5,
    "has_contradictions": boolean,
    "contradictions": ["contradicción 1: dice X pero luego dice Y"],
    "logical_flow": "smooth" | "acceptable" | "problematic"
  }}}}
}}}}

═══════════════════════════════════════════════════════════
EVALUACIÓN GLOBAL
═══════════════════════════════════════════════════════════

ACEPTABILIDAD (decisión binaria):
- acceptable = true SI:
  * hallucination.severity != "critical" AND
  * fidelity_score >= 3 AND
  * completeness >= 3 AND
  * coherence >= 3
- SINO acceptable = false

QUALITY TIER:
- "critical": hallucination critical O fidelity=1
- "poor": algún score = 1-2
- "acceptable": todos scores >= 3, sin critical issues
- "good": promedio scores >= 4, sin major issues
- "excellent": todos scores = 5

OVERALL SCORE: promedio ponderado
- hallucination detectada → -2 puntos si major/critical
- fidelity_score × 0.35
- completeness × 0.25
- relevance × 0.20
- coherence × 0.20

RECOMMENDATION:
- "reject": acceptable=false O critical hallucination
- "review": scores 2-3 O major hallucination
- "approve": acceptable=true AND no major issues

OUTPUT:
{{{{
  "overall_quality": {{{{
    "acceptable": boolean,
    "quality_tier": "excellent" | "good" | "acceptable" | "poor" | "critical",
    "overall_score": float (1.0-5.0),
    "critical_issues": ["issue 1", "issue 2"],
    "recommendation": "approve" | "review" | "reject",
    "reasoning": "Breve explicación de la decisión"
  }}}}
}}}}

═══════════════════════════════════════════════════════════
FORMATO FINAL DE RESPUESTA
═══════════════════════════════════════════════════════════

Devuelve SOLO un objeto JSON válido con esta estructura exacta:

{{{{
  "hallucination_check": {{{{ ... }}}},
  "fidelity_score": {{{{ ... }}}},
  "completeness": {{{{ ... }}}},
  "relevance": {{{{ ... }}}},
  "coherence": {{{{ ... }}}},
  "overall_quality": {{{{ ... }}}}
}}}}

NO agregues texto antes o después del JSON.
NO uses markdown (```json).
Solo el JSON puro.
"""

    def _build_verification_prompt(self, user_question: str, sources: str,
                                   ai_response: str, initial_result: Dict) -> str:
        """Build verification prompt for critical cases"""
        return f"""ALERT: Esta conversación fue flagged por posibles problemas críticos.

CONTEXTO:
- Pregunta usuario: {user_question}
- Fuentes disponibles: {sources}
- Respuesta del AI: {ai_response}

Resultado evaluación inicial:
{json.dumps(initial_result, indent=2, ensure_ascii=False)}

TU TAREA: Verificación profunda de alucinaciones.

INSTRUCCIONES ULTRA-ESTRICTAS:
1. Asume que la evaluación inicial puede estar equivocada
2. Re-lee TODAS las fuentes con extremo cuidado
3. Por CADA oración de la respuesta AI:
   a) ¿Está LITERALMENTE en las fuentes? (no inferencias)
   b) Si es inferencia: ¿es lógicamente válida?
   c) Si menciona URL/email/dato específico: ¿aparece exacto en fuentes?

4. Casos especiales - MARCA COMO ALUCINACIÓN:
   - URLs que no están textualmente en fuentes
   - Emails inventados
   - Números/fechas/nombres no mencionados
   - Pasos de procedimientos no descritos en docs
   - Combinar info de múltiples docs de forma engañosa

5. NO marques como alucinación:
   - Reformulaciones fieles de contenido
   - Conectores lógicos ("por lo tanto", "además")
   - Saludos/cortesías genéricas
   - Resúmenes precisos

OUTPUT (solo JSON):
{{{{
  "verification": {{{{
    "agrees_with_initial": boolean,
    "final_hallucination_detected": boolean,
    "final_severity": "none" | "minor" | "major" | "critical",
    "detailed_evidence": ["extracto exacto 1 con razón", "extracto 2"],
    "confidence": float (0.0-1.0),
    "changed_from_initial": "Qué cambió y por qué"
  }}}}
}}}}

NO agregues texto antes o después del JSON.
"""

    def _verify_critical_case(self, user_question: str, sources: str,
                              ai_response: str, initial_result: Dict) -> Optional[Dict]:
        """Run verification agent on critical cases"""

        prompt = self._build_verification_prompt(user_question, sources, ai_response, initial_result)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            return self._parse_json_response(response.text)
        except Exception as e:
            print(f"  ⚠️  Error in verification: {e}")
            return None

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from model response, handling markdown wrapping"""
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()

        return json.loads(text)

    def evaluate(self, user_question: str, sources: str, ai_response: str,
                 trace_id: str, session_id: str) -> 'EvaluationResult':
        """
        Main evaluation function with Vertex AI

        Returns same EvaluationResult as original evaluator
        """
        # Step 0: Evaluate question quality FIRST
        question_prompt = self._build_question_evaluation_prompt(user_question)

        try:
            question_response = self.model.generate_content(
                question_prompt,
                generation_config=self.generation_config
            )
            question_quality_dict = self._parse_json_response(question_response.text)
        except Exception as e:
            print(f"  ⚠️  Error evaluating question quality for {trace_id}: {e}")
            # Fallback to neutral question quality
            question_quality_dict = {
                'clarity_score': 3,
                'context_completeness': 3,
                'is_ambiguous': False,
                'possible_interpretations': [],
                'question_type': 'unknown',
                'missing_information': [],
                'needs_clarification': False,
                'clarification_needed': [],
                'explanation': 'Question quality evaluation failed'
            }

        # Step 1: Main evaluation (now question-aware)
        prompt = self._build_main_prompt(user_question, sources, ai_response, question_quality_dict)

        try:
            main_response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            result_dict = self._parse_json_response(main_response.text)
        except Exception as e:
            print(f"  ❌ Error in main evaluation for {trace_id}: {e}")
            raise

        # Step 2: Check if verification needed
        needs_verification = (
            result_dict['hallucination_check']['detected'] and
            result_dict['hallucination_check']['severity'] in ['major', 'critical']
        ) or (
            result_dict['overall_quality']['overall_score'] < 3.0
        )

        verification_result = None
        if needs_verification:
            print(f"  ⚠️  Case {trace_id} flagged for verification")
            verification_result = self._verify_critical_case(
                user_question, sources, ai_response, result_dict
            )

            # Update hallucination check with verification results
            if verification_result:
                result_dict['hallucination_check']['detected'] = verification_result['verification']['final_hallucination_detected']
                result_dict['hallucination_check']['severity'] = verification_result['verification']['final_severity']
                if verification_result['verification']['detailed_evidence']:
                    result_dict['hallucination_check']['evidence'] = verification_result['verification']['detailed_evidence']

        # Parse into dataclass
        evaluation = EvaluationResult(
            trace_id=trace_id,
            session_id=session_id,
            question_quality=QuestionQuality(**question_quality_dict),
            hallucination_check=HallucinationCheck(**result_dict['hallucination_check']),
            fidelity_score=FidelityScore(**result_dict['fidelity_score']),
            completeness=Completeness(**result_dict['completeness']),
            relevance=Relevance(**result_dict['relevance']),
            coherence=Coherence(**result_dict['coherence']),
            overall_quality=OverallQuality(**result_dict['overall_quality']),
            verification_applied=needs_verification,
            verification_result=verification_result,
            evaluation_timestamp=datetime.now().isoformat(),
            question_aware_adjustment=result_dict.get('question_aware_adjustment', '')
        )

        return evaluation


# Export same function as original
def evaluation_to_dict(evaluation: EvaluationResult) -> Dict:
    """Import from original evaluator"""
    from ai_evaluator import evaluation_to_dict as original_eval_to_dict
    return original_eval_to_dict(evaluation)


if __name__ == "__main__":
    # Example usage
    print("""
    Vertex AI Gemini Evaluator - Usage Example:

    # Option 1: Using service account key file
    evaluator = VertexGeminiEvaluator(
        project_id="your-gcp-project-id",
        location="us-central1",
        service_account_key_path="/path/to/service-account-key.json"
    )

    # Option 2: Using Application Default Credentials (for GCP environments)
    evaluator = VertexGeminiEvaluator(
        project_id="your-gcp-project-id",
        location="us-central1"
    )

    # Then use normally:
    result = evaluator.evaluate(
        user_question="...",
        sources="...",
        ai_response="...",
        trace_id="...",
        session_id="..."
    )
    """)
