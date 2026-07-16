"""
Quick test script for Vertex AI Evaluator
Run this after setting up your GCP project and credentials
"""

import os
from ai_evaluator_vertex import VertexGeminiEvaluator, evaluation_to_dict

# Configuration - Update these with your values
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'your-project-id')
GCP_LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
SERVICE_ACCOUNT_KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def test_vertex_evaluator():
    """Test the Vertex AI evaluator with a simple example"""

    print("=" * 60)
    print("VERTEX AI GEMINI EVALUATOR - TEST")
    print("=" * 60)

    # Initialize evaluator
    print("\n1. Initializing Vertex AI Evaluator...")
    try:
        if SERVICE_ACCOUNT_KEY_PATH:
            evaluator = VertexGeminiEvaluator(
                project_id=GCP_PROJECT_ID,
                location=GCP_LOCATION,
                service_account_key_path=SERVICE_ACCOUNT_KEY_PATH
            )
        else:
            # Use Application Default Credentials
            evaluator = VertexGeminiEvaluator(
                project_id=GCP_PROJECT_ID,
                location=GCP_LOCATION
            )
        print("✅ Evaluator initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing evaluator: {e}")
        print("\nMake sure you have:")
        print("  1. Set GCP_PROJECT_ID environment variable")
        print("  2. Set GOOGLE_APPLICATION_CREDENTIALS or run 'gcloud auth application-default login'")
        print("  3. Enabled Vertex AI API: gcloud services enable aiplatform.googleapis.com")
        return

    # Test case
    print("\n2. Running test evaluation...")
    test_question = "¿Cuáles son los requisitos para abrir una cuenta de ahorros?"
    test_sources = """
    Requisitos Cuenta de Ahorros - Davivienda

    Para persona natural:
    1. Cédula de ciudadanía original
    2. Certificado laboral o comprobante de ingresos
    3. Depósito mínimo de apertura: $50,000
    4. Diligenciar formulario de vinculación

    Documentación adicional si aplica:
    - Si es independiente: RUT y declaración de renta
    - Si es pensionado: certificado de pensión
    """

    test_response = """
    Para abrir una cuenta de ahorros en Davivienda como persona natural necesitas:

    1. Cédula de ciudadanía original
    2. Certificado laboral o comprobante de ingresos
    3. Realizar un depósito mínimo de $50,000
    4. Completar el formulario de vinculación

    Si eres trabajador independiente, también necesitarás el RUT y declaración de renta.
    Si eres pensionado, el certificado de pensión.

    ¿Te gustaría información sobre los tipos de cuenta de ahorros disponibles?
    """

    try:
        evaluation = evaluator.evaluate(
            user_question=test_question,
            sources=test_sources,
            ai_response=test_response,
            trace_id="test-001",
            session_id="test-session"
        )

        print("✅ Evaluation completed successfully!")

        # Display results
        print("\n" + "=" * 60)
        print("EVALUATION RESULTS")
        print("=" * 60)

        print(f"\n📝 Question Quality:")
        print(f"   Clarity Score: {evaluation.question_quality.clarity_score}/5")
        print(f"   Needs Clarification: {evaluation.question_quality.needs_clarification}")

        print(f"\n🔍 Hallucination Check:")
        print(f"   Detected: {evaluation.hallucination_check.detected}")
        print(f"   Severity: {evaluation.hallucination_check.severity}")

        print(f"\n⚖️  Quality Scores:")
        print(f"   Fidelity: {evaluation.fidelity_score.score}/5")
        print(f"   Completeness: {evaluation.completeness.score}/5")
        print(f"   Relevance: {evaluation.relevance.score}/5")
        print(f"   Coherence: {evaluation.coherence.score}/5")

        print(f"\n📊 Overall Assessment:")
        print(f"   Overall Score: {evaluation.overall_quality.overall_score:.2f}/5.0")
        print(f"   Quality Tier: {evaluation.overall_quality.quality_tier}")
        print(f"   Recommendation: {evaluation.overall_quality.recommendation}")
        print(f"   Acceptable: {evaluation.overall_quality.acceptable}")

        if evaluation.verification_applied:
            print(f"\n⚠️  Verification Applied: Yes")

        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY! ✅")
        print("=" * 60)

        # Convert to dict format
        result_dict = evaluation_to_dict(evaluation)
        print(f"\n✅ Conversion to dict successful ({len(result_dict)} fields)")

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n✅ All tests passed! Vertex AI evaluator is ready to use.")
    print("\nNext steps:")
    print("  1. Update run_ai_evaluation.ipynb to use VertexGeminiEvaluator")
    print("  2. Run full evaluation on your dataset")
    print("  3. Monitor usage in GCP Console: https://console.cloud.google.com/vertex-ai")


if __name__ == "__main__":
    test_vertex_evaluator()
